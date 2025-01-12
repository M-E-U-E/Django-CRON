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


# Utility classes for CSV handling and chart data preparation
class CSVHandler:
    @staticmethod
    def validate_csv(file):
        """
        Validate the uploaded file to ensure it is a CSV.
        """
        if not file:
            return "No file selected. Please upload a CSV file."
        if not file.name.endswith('.csv'):
            return "Invalid file format. Please upload a CSV file."
        return None

    @staticmethod
    def write_csv(response, queryset):
        """
        Write the queryset to a CSV file for export.
        """
        writer = csv.writer(response)
        writer.writerow([
            'LeadId', 'LeadDate', 'LeadCheckin', 'LeadCheckout',
            'Revenue', 'Commission', 'Hotel Location'
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


class ChartDataPreparer:
    @staticmethod
    def prepare_line_chart_data(queryset):
        """
        Prepare data for the line chart showing monthly revenue.
        """
        return [
            {
                'x': record['month'].isoformat() if record['month'] else '',
                'y': float(record['total_revenue']) if record['total_revenue'] else 0.0,
            }
            for record in queryset
        ]

    @staticmethod
    def prepare_pie_chart_data(queryset):
        """
        Prepare data for the pie chart showing revenue by hotel country.
        Countries contributing less than 6% are grouped under "Others".
        """
        total_revenue_all = sum(
            float(item['total_revenue']) if item['total_revenue'] else 0.0
            for item in queryset
        )
        pie_labels, pie_values, others_total = [], [], 0.0

        for item in queryset:
            country = item['hotel_country'] or 'Unknown'
            revenue = float(item['total_revenue']) if item['total_revenue'] else 0.0
            share = revenue / total_revenue_all if total_revenue_all else 0.0

            if share < 0.06:
                others_total += revenue
            else:
                pie_labels.append(country)
                pie_values.append(revenue)

        if others_total > 0:
            pie_labels.append('Others')
            pie_values.append(others_total)

        return pie_labels, pie_values


@admin.register(KayakTransaction)
class KayakTransactionAdmin(ModelAdmin):
    list_display = (
        'lead_id', 'lead_date', 'lead_checkin', 'lead_checkout',
        'revenue', 'commission', 'hotel_location_status'
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
        line_chart_data = ChartDataPreparer.prepare_line_chart_data(monthly_revenue_qs)

        # --------------------------------------------------------------------
        # 2. Revenue by Hotel Country (Pie Chart), grouping < 8% as "Others"
        # --------------------------------------------------------------------
        country_revenue_qs = (
            KayakTransaction.objects
            .values('hotel_country')
            .annotate(total_revenue=Sum('revenue'))
            .order_by('-total_revenue')
        )

        # Prepare pie chart labels and values
        pie_labels, pie_values = ChartDataPreparer.prepare_pie_chart_data(country_revenue_qs)

        # --------------------------------------------------------------------
        # 3. Serialize data for Chart.js
        # --------------------------------------------------------------------
        extra_context = extra_context or {}
        extra_context.update({
            'custom_import_csv_url': 'import-csv/',
            'line_chart_data': json.dumps(line_chart_data, cls=DjangoJSONEncoder),
            'pie_labels': json.dumps(pie_labels, cls=DjangoJSONEncoder),
            'pie_values': json.dumps(pie_values, cls=DjangoJSONEncoder),
        })

        return super().changelist_view(request, extra_context=extra_context)

    def import_csv_view(self, request):
        """
        Custom admin view for importing CSV files.
        """
        if request.method == "POST":
            file = request.FILES.get('csv_file')
            # Validate the uploaded CSV file
            error_message = CSVHandler.validate_csv(file)
            if error_message:
                self._send_message(request, error_message, messages.ERROR)
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
        CSVHandler.write_csv(response, queryset)
        return response

    export_as_csv.short_description = "Export Selected as CSV"
