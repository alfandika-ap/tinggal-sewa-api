from django.contrib.auth.models import User
from django.db import models
import json
from typing import Optional, List

from core.models import BaseModel


# Create your models here.
class Customer(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return self.fullname


class Kost(BaseModel):
    title = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    facilities = models.TextField()  # Stored as JSON string
    rules = models.TextField()  # Stored as JSON string
    contact = models.CharField(max_length=255)
    url = models.URLField()
    image_url = models.URLField(null=True, blank=True)
    gender = models.CharField(max_length=50)
    
    def get_facilities(self) -> List[str]:
        return json.loads(self.facilities) if self.facilities else []
    
    def set_facilities(self, facilities_list: List[str]):
        self.facilities = json.dumps(facilities_list)
    
    def get_rules(self) -> List[str]:
        return json.loads(self.rules) if self.rules else []
    
    def set_rules(self, rules_list: List[str]):
        self.rules = json.dumps(rules_list)
    
    def __str__(self):
        return self.title


class Bookmark(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    kost = models.ForeignKey(Kost, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'kost')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.kost.title}"
