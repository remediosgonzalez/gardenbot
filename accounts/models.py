from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Account(models.Model):
    user = models.OneToOneField(User, models.SET_NULL, null=True)
    balance = models.IntegerField(default=0)
