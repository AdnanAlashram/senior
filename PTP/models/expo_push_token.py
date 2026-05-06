from django.db import models
from PTP.models.user import User


class ExpoPushToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='expo_token')
    token = models.CharField(max_length=255, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.token}" 