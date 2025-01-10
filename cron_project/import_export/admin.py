from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path
from django.contrib import messages
from django.shortcuts import render
import csv
import sys
from io import TextIOWrapper
from .utils import CSVDataImporter
from .models import KayakTransaction


@admin.register(KayakTransaction)
class KayakTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'lead_id',
        'lead_date',
        'lead_checkin',
        'lead_checkout',
        'revenue',
        'commission',
        'hotel_location_status'
    )
    search_fields = ('lead_id', 'hotel_city', 'hotel_country')
    list_filter = ('lead_date', 'lead_checkin', 'lead_checkout')
    actions = ['export_as_csv']

    def get_urls(self):
        """
        Add a custom URL for the CSV import feature.
        """
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.import_csv_view, name='kayaktransaction_import_csv'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        """
        Add an "Import CSV" button to the changelist view.
        """
        extra_context = extra_context or {}
        extra_context['custom_import_csv_url'] = 'import-csv/'
        return super().changelist_view(request, extra_context=extra_context)

    def import_csv_view(self, request):
        """
        Custom admin view for importing CSV files.
        """
        if request.method == "POST":
            file = request.FILES.get('csv_file')
            if not file:
                self._send_message(request, "No file selected. Please upload a CSV file.", messages.ERROR)
                return HttpResponseRedirect("../")

            if not file.name.endswith('.csv'):
                self._send_message(request, "Invalid file format. Please upload a CSV file.", messages.ERROR)
                return HttpResponseRedirect("../")

            try:
                # Read the CSV file with UTF-8 encoding
                csv_file = TextIOWrapper(file.file, encoding='utf-8')
                
                # Use the CSVDataImporter class to process the file
                from .utils import CSVDataImporter
                import_results = CSVDataImporter.import_csv_data(csv_file)
                
                # Check for error key in the returned dictionary
                if 'error' in import_results:
                    self._send_message(request, f"Error importing CSV: {import_results['error']}", messages.ERROR)
                    return HttpResponseRedirect("../")
                
                # Provide feedback based on the import results
                success_count = import_results.get('success_count', 0)
                error_count = import_results.get('error_count', 0)

                if success_count > 0:
                    self._send_message(request, f"Successfully imported {success_count} records.", messages.SUCCESS)
                if error_count > 0:
                    self._send_message(request, f"{error_count} records failed to import.", messages.WARNING)
            except Exception as e:
                self._send_message(request, f"Unexpected error: {e}", messages.ERROR)

            return HttpResponseRedirect("../")

        return render(request, 'admin/import_csv_form.html', context={'title': 'Import CSV'})



    @staticmethod
    def _import_csv_data(csv_file, request):
        """
        Static method to handle CSV data import logic.
        """
        CSVDataImporter.import_csv_data(csv_file)
        messages.success(request, "CSV data imported successfully.")

    @staticmethod
    def _send_message(request, message, level):
        """
        Utility method to send messages to the admin interface.
        """
        messages.add_message(request, level, message)

    def export_as_csv(self, request, queryset):
        """
        Export selected transactions as a CSV file.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="kayak_transactions.csv"'
        self._write_csv(response, queryset)
        return response

    @staticmethod
    def _write_csv(response, queryset):
        """
        Static method to handle writing data to a CSV file.
        """
        writer = csv.writer(response)
        writer.writerow([
            'LeadId',
            'LeadDate',
            'LeadCheckin',
            'LeadCheckout',
            'Revenue',
            'Commission',
            'Hotel Location'
        ])
        for transaction in queryset:
            writer.writerow([
                transaction.lead_id,
                transaction.lead_date,
                transaction.lead_checkin,
                transaction.lead_checkout,
                transaction.revenue,
                transaction.commission,
                transaction.hotel_location_status
            ])

    export_as_csv.short_description = "Export Selected as CSV"
