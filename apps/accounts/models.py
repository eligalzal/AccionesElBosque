from django.db import models

class Usuarios(models.Model):
    username = models.CharField(primary_key=True, max_length=50)
    passw = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    street_address = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    interest1 = models.CharField(max_length=4, blank=True, null=True)
    interest2 = models.CharField(max_length=4, blank=True, null=True)
    interest3 = models.CharField(max_length=4, blank=True, null=True)
    kyc_status = models.CharField(max_length=50, blank=True, null=True)
    alpaca_account_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuarios'