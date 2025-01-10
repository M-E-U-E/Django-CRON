import pandas as pd
from datetime import datetime
from django.utils.timezone import make_aware
from .models import KayakTransaction
from .db_modules.upsert_transactions import upsert_transaction_data


class CSVDataImporter:
    """
    Utility class for importing CSV data into the KayakTransaction model.
    Includes date parsing, hotel data validation, and record creation/updating.
    """

    @staticmethod
    def import_csv_data(csv_file):
        """
        Main method to import CSV data into the database.
        Returns a dictionary with counts of successes and errors.
        """
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return {'success_count': 0, 'error_count': 1, 'error': str(e)}

        try:
            df = CSVDataImporter._process_dataframe(df)
        except Exception as e:
            print(f"Error processing DataFrame: {e}")
            return {'success_count': 0, 'error_count': len(df) if 'df' in locals() else 1, 'error': str(e)}

        success_count, error_count = 0, 0

        for _, row in df.iterrows():
            try:
                upsert_transaction_data(
                    lead_id=row['LeadId'],
                    lead_date=row['LeadDate'],
                    lead_checkin=row['LeadCheckin'],
                    lead_checkout=row['LeadCheckout'],
                    revenue=row['Revenue'],
                    commission=row['Commission'],
                    hotel_id=None,  # Assuming hotel_id is not available in the CSV
                    hotel_country=row['HotelCountry'],
                    hotel_city=row['HotelCity']
                )
                success_count += 1
            except Exception as e:
                print(f"Error processing row with LeadId {row.get('LeadId', 'Unknown')}: {e}")
                error_count += 1

        return {'success_count': success_count, 'error_count': error_count}

    @staticmethod
    def _process_dataframe(df):
        """
        Processes the DataFrame: applies data transformations and validations.
        """
        # Apply date parsing
        for date_column in ['LeadDate', 'LeadCheckin', 'LeadCheckout']:
            df[date_column] = df[date_column].apply(CSVDataImporter._parse_date)

        # Clean and validate hotel data
        df[['HotelCountry', 'HotelCity']] = df[['HotelCountry', 'HotelCity']].apply(
            lambda row: CSVDataImporter._clean_hotel_data(row['HotelCountry'], row['HotelCity']),
            axis=1, result_type='expand'
        )

        # Ensure Revenue and Commission are numeric
        df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce').fillna(0.0)
        df['Commission'] = pd.to_numeric(df['Commission'], errors='coerce').fillna(0.0)

        return df

    @staticmethod
    def _parse_date(date_str):
        """
        Parses date strings with multiple format attempts.
        Returns timezone-aware datetime or None if parsing fails.
        """
        if pd.isna(date_str) or not isinstance(date_str, str):
            return None

        formats = [
            '%d/%m/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y %H:%M', '%m/%d/%Y %H:%M', '%Y-%m-%d %H:%M'
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return make_aware(dt)
            except (ValueError, AttributeError):
                continue
        return None

    @staticmethod
    def _clean_hotel_data(hotel_country, hotel_city):
        """
        Validates and cleans hotel data (country, city).
        """
        hotel_country = str(hotel_country).strip() if pd.notna(hotel_country) else None
        hotel_city = str(hotel_city).strip() if pd.notna(hotel_city) else None

        return hotel_country, hotel_city
