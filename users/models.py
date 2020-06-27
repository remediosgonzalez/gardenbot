from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_bot = models.BooleanField()
    language_code = models.CharField(max_length=255)
