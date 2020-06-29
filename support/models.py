from django.contrib.auth import get_user_model
from django.db import models


class SupportTicket(models.Model):
    from_user = models.ForeignKey(get_user_model(), models.SET_NULL, null=True)
    text = models.TextField()

    user_message_id = models.IntegerField(null=True)
    manager_message_id = models.IntegerField(null=True)

    is_resolved = models.BooleanField(default=False)

    date_created = models.DateTimeField(auto_now_add=True)
    date_resolved = models.DateTimeField(null=True, blank=True)
