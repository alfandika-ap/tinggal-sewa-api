from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from core.models import BaseModel


# Create your models here.
class ChatMessages(BaseModel):
    role = models.CharField(max_length=255)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token_usage = models.IntegerField(default=0)
    function_name = models.CharField(max_length=255, null=True, blank=True)