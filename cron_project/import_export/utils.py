from datetime import datetime
from .models import KayakTransaction

def import_csv_data(csv_file):
    """
    Import CSV data into KayakTransaction model with date parsing and hotel data validation.
    Handles null/blank/negative values for hotel fields.
    """
    import csv
    reader = csv.DictReader(csv_file)

    for row in reader:
        try:
            # Parse and convert datetime fields
            lead_date = datetime.strptime(row['LeadDate'], '%d/%m/%Y %H:%M:%S')
            lead_checkin = datetime.strptime(row['LeadCheckin'], '%d/%m/%Y %H:%M:%S')
            lead_checkout = datetime.strptime(row['LeadCheckout'], '%d/%m/%Y %H:%M:%S')

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