from django.db import models
from django.contrib.auth.models import User

class AlpacaBrokerAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    alpaca_account_id = models.CharField(max_length=100)
    email = models.EmailField()
    kyc_status = models.CharField(max_length=50, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Alpaca ID: {self.alpaca_account_id}"

