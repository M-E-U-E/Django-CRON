from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
import csv
from datetime import datetime
from .models import Transaction

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('agent_id', 'lead_date', 'home_city', 'home_country', 'boom_score', 
                   'transaction_type', 'transaction_status', 'flag')
    search_fields = ('agent_id', 'home_city', 'home_country', 'pnr')
    list_filter = ('home_country', 'language_code', 'transaction_status', 'device_category')
    change_list_template = 'admin/transaction_changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.import_csv, name='import-csv'),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES.get("csv_file")
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a CSV file')
                return redirect("..")

            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            for row in reader:
                try:
                    # Convert date strings to datetime objects
                    lead_date = datetime.strptime(row['LeadDate'], '%m/%d/%Y %H:%M:%S') if row['LeadDate'] else None
                    lead_check_in = datetime.strptime(row['LeadCheckIn'], '%m/%d/%Y %H:%M:%S') if row['LeadCheckIn'] else None
                    lead_check_out = datetime.strptime(row['LeadCheckOut'], '%m/%d/%Y %H:%M:%S') if row['LeadCheckOut'] else None

                    Transaction.objects.update_or_create(
                        agent_id=row['AgentId'],  # Primary key
                        defaults={
                            'lead_date': lead_date,
                            'lead_check_in': lead_check_in,
                            'lead_check_out': lead_check_out,
                            'meeting_id': row.get('MeetingId'),
                            'boom_score': float(row['BoomScore']) if row['BoomScore'] else None,
                            'boom_score_delta': float(row['BoomScoreDelta']) if row['BoomScoreDelta'] else None,
                            'boom_score_delta_bucket': row.get('BoomScoreDeltaBucket'),
                            'conversation': row.get('Conversation'),
                            'language_code': row.get('LanguageCode'),
                            'device_category': row.get('DeviceCategory'),
                            'country_city_code': row.get('CountryCityCode'),
                            'brand_id': row.get('BrandID'),
                            'lifter': row.get('Lifter'),
                            'home_city': row.get('HomeCity'),
                            'home_country': row.get('HomeCountry'),
                            'home_name': row.get('HomeName'),
                            'payment_method': row.get('PaymentMethod'),
                            'transaction_type': row.get('TransactionType'),
                            'transaction_status': row.get('TransactionStatus'),
                            'transaction_status_value': row.get('TransactionStatusValue'),
                            'flag': row.get('Flag'),
                            'pnr': row.get('Pnr')
                        }
                    )
                except Exception as e:
                    messages.error(request, f'Error importing row: {str(e)}')
                    continue

            messages.success(request, 'CSV file imported successfully')
            return redirect("..")

        return render(request, 'admin/csv_form.html')

admin.site.register(Transaction, TransactionAdmin)