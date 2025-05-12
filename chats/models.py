from django.db import models

# Create your models here.
from core.models import BaseModel
from django.contrib.auth.models import User

# Create your models here.
class ChatMessages(BaseModel):
    role = models.CharField(max_length=255)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
