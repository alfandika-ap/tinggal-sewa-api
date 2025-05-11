from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel


# Create your models here.
class Customer(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return self.fullname
    
