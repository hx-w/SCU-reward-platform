from django.db import models
from django.utils import timezone
# Create your models here.

class ChatMess(models.Model):
    sender = models.CharField(max_length=128, null=True)
    send_time = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=128, default="None")
    sended = models.BooleanField(default=False)

    def __str__(self):
        return self.sender
    