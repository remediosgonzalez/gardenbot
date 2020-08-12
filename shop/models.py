from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Item(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    price = models.BigIntegerField(null=True)
    photo_file_id = models.TextField(null=True)

    disabled = models.BooleanField(default=False)
    created_by_user = models.ForeignKey(User, models.SET_NULL, null=True)

    @property
    def is_active(self):
        return True if self.name and self.price and not self.disabled else False


class Order(models.Model):
    user = models.ForeignKey(User, models.SET_NULL, null=True)
    price = models.FloatField()
    address = models.TextField()
    status = models.CharField(max_length=255, blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(blank=True, null=True)


class OrderItem(models.Model):
    item = models.ForeignKey(Item, models.SET_NULL, null=True)
    order = models.ForeignKey(Order, models.CASCADE)
    quantity = models.SmallIntegerField(default=1)


class ShippingPolicy(models.Model):
    text = models.TextField()
    updated = models.DateTimeField(auto_now_add=True)
