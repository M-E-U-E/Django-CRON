# admin.py

from django.contrib import admin, messages
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.core.serializers.json import DjangoJSONEncoder
import json
import csv
from io import TextIOWrapper

from unfold.admin import ModelAdmin
from .models import KayakTransaction
from .utils import CSVDataImporter


@admin.register(KayakTransaction)
class KayakTransactionAdmin(ModelAdmin):
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
        Add an "Import CSV" button and supply dynamic chart data to the changelist view.
        """
        # --------------------------------------------------------------------
        # 1. Monthly Revenue for the Line Chart
        # --------------------------------------------------------------------
        monthly_revenue_qs = (
            KayakTransaction.objects
            .annotate(month=TruncMonth('lead_date'))
            .values('month')
            .annotate(total_revenue=Sum('revenue'))
            .order_by('month')
        )

        # Convert the queryset into a list of { x, y } for Chart.js
        # x = month (as ISO8601 string), y = total_revenue
        line_chart_data = [
            {
                'x': record['month'].isoformat() if record['month'] else '',
                'y': float(record['total_revenue']) if record['total_revenue'] else 0.0,
            }
            for record in monthly_revenue_qs
        ]

        # --------------------------------------------------------------------
        # 2. Revenue by Hotel Country (Pie Chart), grouping < 8% as "Others"
        # --------------------------------------------------------------------
        country_revenue_qs = (
            KayakTransaction.objects
            .values('hotel_country')
            .annotate(total_revenue=Sum('revenue'))
            .order_by('-total_revenue')
        )

        # Calculate total revenue across all countries, converting to float
        total_revenue_all = sum(
            float(item['total_revenue']) if item['total_revenue'] else 0.0
            for item in country_revenue_qs
        )

        # Prepare pie chart labels and values
        pie_labels = []
        pie_values = []
        others_total = 0.0  # Accumulate all countries < 8% here

        for item in country_revenue_qs:
            country = item['hotel_country'] or 'Unknown'
            revenue = float(item['total_revenue']) if item['total_revenue'] else 0.0
            share = revenue / total_revenue_all if total_revenue_all else 0.0

            if share < 0.06:
                # Group this country's share into "Others"
                others_total += revenue
            else:
                pie_labels.append(country)
                pie_values.append(revenue)

        # If we have accumulated anything in 'Others', add it
        if others_total > 0:
            pie_labels.append('Others')
            pie_values.append(others_total)

        # --------------------------------------------------------------------
        # 3. Serialize data for Chart.js
        # --------------------------------------------------------------------
        extra_context = extra_context or {}
        extra_context['custom_import_csv_url'] = 'import-csv/'
        extra_context['line_chart_data'] = json.dumps(line_chart_data, cls=DjangoJSONEncoder)
        extra_context['pie_labels'] = json.dumps(pie_labels, cls=DjangoJSONEncoder)
        extra_context['pie_values'] = json.dumps(pie_values, cls=DjangoJSONEncoder)

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

        # Show a simple form prompting user to upload CSV
        return render(request, 'admin/import_csv_form.html', context={'title': 'Import CSV'})

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
