from import_export.models import KayakTransaction

def upsert_transaction_data(lead_id, lead_date, lead_checkin, lead_checkout, revenue, commission, hotel_id, hotel_country, hotel_city):
    KayakTransaction.objects.update_or_create(
        lead_id=lead_id,
        defaults={
            'lead_date': lead_date,
            'lead_checkin': lead_checkin,
            'lead_checkout': lead_checkout,
            'revenue': revenue,
            'commission': commission,
            'hotel_country': hotel_country,
            'hotel_city': hotel_city,
        }
    )
