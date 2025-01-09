from datetime import datetime
from .models import KayakTransaction

def import_csv_data(csv_file):
    """
    Import CSV data into KayakTransaction model with date parsing and hotel data validation.
    Handles null/blank/negative values for hotel fields.
    """
    import csv
    reader = csv.DictReader(csv_file)

    def parse_date(date_str):
        """Helper function to parse dates with multiple format attempts"""
        formats = [
            '%d/%m/%Y %H:%M:%S',  # DD/MM/YYYY HH:MM:SS
            '%m/%d/%Y %H:%M:%S',  # MM/DD/YYYY HH:MM:SS
            '%Y-%m-%d %H:%M:%S'   # YYYY-MM-DD HH:MM:SS
        ]
        
        for date_format in formats:
            try:
                return datetime.strptime(date_str, date_format)
            except ValueError:
                continue
        
        raise ValueError(f"Time data '{date_str}' does not match any expected formats")

    for row in reader:
        try:
            # Parse and convert datetime fields with multiple format attempts
            try:
                lead_date = parse_date(row['LeadDate'])
                lead_checkin = parse_date(row['LeadCheckin'])
                lead_checkout = parse_date(row['LeadCheckout'])
            except ValueError as e:
                print(f"Date parsing error for LeadId {row.get('LeadId', 'Unknown')}: {str(e)}")
                continue

            # Process hotel ID - handle empty, non-numeric, and negative values
            try:
                hotel_id = int(row.get('HotelID', '-100'))
                if hotel_id < 0:
                    hotel_id = None
            except (ValueError, TypeError):
                hotel_id = None

            # Process hotel country and city - handle empty or whitespace values
            hotel_country = row.get('HotelCountry', '').strip() or None
            hotel_city = row.get('HotelCity', '').strip() or None

            # Handle special cases like 'Not Applicable'
            if hotel_country == 'Not Applicable':
                hotel_country = None
            if hotel_city == 'Not Applicable':
                hotel_city = None

            # Create or update KayakTransaction
            KayakTransaction.objects.update_or_create(
                lead_id=row['LeadId'],
                defaults={
                    'lead_date': lead_date,
                    'lead_checkin': lead_checkin,
                    'lead_checkout': lead_checkout,
                    'revenue': float(row['Revenue']),
                    'commission': float(row['Commission']),
                    'hotel_id': hotel_id,
                    'hotel_country': hotel_country,
                    'hotel_city': hotel_city,
                },
            )
        except Exception as e:
            # Log errors with more context
            print(f"Error processing row with LeadId {row.get('LeadId', 'Unknown')}:")
            print(f"Row data: {row}")
            print(f"Error: {str(e)}")
            continue