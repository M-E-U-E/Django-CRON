from django.db import models

class Transaction(models.Model):
    agent_id = models.CharField(max_length=100, unique=True)
    lead_date = models.DateTimeField(null=True, blank=True)
    lead_check_in = models.DateTimeField(null=True, blank=True)
    lead_check_out = models.DateTimeField(null=True, blank=True)
    meeting_id = models.CharField(max_length=100, null=True, blank=True)
    boom_score = models.FloatField(null=True, blank=True)
    boom_score_delta = models.FloatField(null=True, blank=True)
    boom_score_delta_bucket = models.CharField(max_length=100, null=True, blank=True)
    conversation = models.CharField(max_length=100, null=True, blank=True)
    language_code = models.CharField(max_length=10, null=True, blank=True)
    device_category = models.CharField(max_length=50, null=True, blank=True)
    country_city_code = models.CharField(max_length=100, null=True, blank=True)
    brand_id = models.CharField(max_length=50, null=True, blank=True)
    lifter = models.CharField(max_length=50, null=True, blank=True)
    home_city = models.CharField(max_length=100, null=True, blank=True)
    home_country = models.CharField(max_length=100, null=True, blank=True)
    home_name = models.CharField(max_length=100, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    transaction_type = models.CharField(max_length=50, null=True, blank=True)
    transaction_status = models.CharField(max_length=50, null=True, blank=True)
    transaction_status_value = models.CharField(max_length=50, null=True, blank=True)
    flag = models.CharField(max_length=50, null=True, blank=True)
    pnr = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Transaction {self.agent_id}"

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"