from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_bot = models.BooleanField()
    language_code = models.CharField(max_length=255)
    is_referral_of_user = models.ForeignKey('self', models.SET_NULL, null=True, blank=True)
