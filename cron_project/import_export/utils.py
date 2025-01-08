from datetime import datetime
from .models import KayakTransaction

def import_csv_data(csv_file):
    """
    Import CSV data into KayakTransaction model with date parsing.
    """
    import csv
    reader = csv.DictReader(csv_file)

    for row in reader:
        try:
            # Parse and convert datetime fields
            lead_date = datetime.strptime(row['LeadDate'], '%d/%m/%Y %H:%M:%S')
            lead_checkin = datetime.strptime(row['LeadCheckin'], '%d/%m/%Y %H:%M:%S')
            lead_checkout = datetime.strptime(row['LeadCheckout'], '%d/%m/%Y %H:%M:%S')

            # Create or update KayakTransaction
            KayakTransaction.objects.update_or_create(
                lead_id=row['LeadId'],
                defaults={
                    'lead_date': lead_date,
                    'lead_checkin': lead_checkin,
                    'lead_checkout': lead_checkout,
                    'revenue': float(row['Revenue']),
                    'commission': float(row['Commission']),
                },
            )
        except Exception as e:
            # Log errors or handle them appropriately
            print(f"Error processing row: {row}, Error: {e}")
