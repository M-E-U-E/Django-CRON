from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path
from django.contrib import messages
from django.shortcuts import render
import csv
from io import TextIOWrapper
from .utils import import_csv_data  # Helper function for CSV data processing
from .models import KayakTransaction

@admin.register(KayakTransaction)
class KayakTransactionAdmin(admin.ModelAdmin):
    list_display = ('lead_id', 'lead_date', 'lead_checkin', 'lead_checkout', 'revenue', 'commission')
    actions = ['export_as_csv']

    def get_urls(self):
        """
        Add a custom URL for the CSV import feature.
        """
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.import_csv_view, name='kayaktransaction_import_csv'),  # Unique path
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        """
        Add an "Import CSV" button to the changelist view.
        """
        extra_context = extra_context or {}
        extra_context['custom_import_csv_url'] = 'import-csv/'  # Link to custom import CSV URL
        return super().changelist_view(request, extra_context=extra_context)

    def import_csv_view(self, request):
        """
        Custom admin view for importing CSV files.
        """
        if request.method == "POST":
            file = request.FILES.get('csv_file')
            if file and file.name.endswith('.csv'):
                try:
                    # Decode file and parse CSV data
                    csv_file = TextIOWrapper(file.file, encoding='utf-8')
                    import_csv_data(csv_file)
                    self.message_user(request, "CSV data imported successfully.", level=messages.SUCCESS)
                except Exception as e:
                    self.message_user(request, f"Error importing CSV: {e}", level=messages.ERROR)
                return HttpResponseRedirect("../")
            self.message_user(request, "Invalid file format. Please upload a CSV file.", level=messages.ERROR)

        # Render the form
        return render(request, 'admin/import_csv_form.html', context={'title': 'Import CSV'})

    def export_as_csv(self, request, queryset):
        """
        Export selected transactions as a CSV file.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="kayak_transactions.csv"'
        writer = csv.writer(response)
        writer.writerow(['LeadId', 'LeadDate', 'LeadCheckin', 'LeadCheckout', 'Revenue', 'Commission'])
        for transaction in queryset:
            writer.writerow([
                transaction.lead_id,
                transaction.lead_date,
                transaction.lead_checkin,
                transaction.lead_checkout,
                transaction.revenue,
                transaction.commission,
                
            ])
        return response

    export_as_csv.short_description = "Export Selected as CSV"


# @admin.register(TransactionMetadata)
# class TransactionMetadataAdmin(admin.ModelAdmin):
#     list_display = ('transaction', 'created_at', 'updated_at')
#     readonly_fields = ('created_at', 'updated_at')
