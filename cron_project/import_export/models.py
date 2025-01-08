from django.db import models

# Main model for the Kayak transaction report
class KayakTransaction(models.Model):
    lead_id = models.CharField(max_length=255, unique=True, verbose_name="Lead ID")
    lead_date = models.DateTimeField(verbose_name="Lead Date")
    lead_checkin = models.DateTimeField(verbose_name="Lead Check-in")
    lead_checkout = models.DateTimeField(verbose_name="Lead Checkout")
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Kayak Transaction"
        verbose_name_plural = "Kayak Transactions"

    def __str__(self):
        return self.lead_id


# # Transaction metadata model
# class TransactionMetadata(models.Model):
#     transaction = models.OneToOneField(KayakTransaction, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creation Time")
#     updated_at = models.DateTimeField(auto_now=True, verbose_name="Update Time")

#     class Meta:
#         verbose_name = "Transaction Metadata"
#         verbose_name_plural = "Transaction Metadata"

#     def __str__(self):
#         return f"Metadata for {self.transaction.lead_id}"
