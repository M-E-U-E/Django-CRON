from django.db import models

class KayakTransaction(models.Model):
    lead_id = models.CharField(max_length=255, unique=True, verbose_name="Lead ID")
    lead_date = models.DateTimeField(verbose_name="Lead Date")
    lead_checkin = models.DateTimeField(verbose_name="Lead Check-in")
    lead_checkout = models.DateTimeField(verbose_name="Lead Checkout")
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)
    hotel_country = models.CharField(max_length=100, null=True, blank=True, verbose_name="Hotel Country")
    hotel_city = models.CharField(max_length=100, null=True, blank=True, verbose_name="Hotel City")
    hotel_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="Hotel ID")  # NEW FIELD

    @property
    def hotel_location_status(self):
        """
        Returns a formatted location string or 'None' if the location data is invalid.
        """
        if self._is_location_invalid():
            return 'None'
        return self._format_location()

    def _is_location_invalid(self):
        """
        Check if the location data is invalid (e.g., missing, invalid, or negative hotel_id).
        """
        return (
            not self.hotel_country or not self.hotel_city or  # Missing country or city
            self.hotel_country.strip() == '' or self.hotel_city.strip() == ''  # Empty country or city
        )

    def _format_location(self):
        """
        Format the hotel location string.
        """
        return f"{self.hotel_city}, {self.hotel_country}"

    class Meta:
        verbose_name = "Kayak Transaction"
        verbose_name_plural = "Kayak Transactions"

    def __str__(self):
        return self.lead_id
