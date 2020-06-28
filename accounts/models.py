from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Account(models.Model):
    user = models.OneToOneField(User, models.SET_NULL, null=True)
    balance = models.FloatField(default=0)


class WalletSweep(models.Model):
    user = models.ForeignKey(User, models.SET_NULL, null=True)
    from_wallet = models.CharField(max_length=255)
    amount = models.FloatField()
