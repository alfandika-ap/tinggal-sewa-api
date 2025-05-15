from django.db import models
from django.utils import timezone

class Property(models.Model):
    property_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    bedroom_count = models.IntegerField(null=True, blank=True)
    bathroom_count = models.IntegerField(null=True, blank=True)
    property_type = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.property_id}"

class ScrappingLog(models.Model):
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50)
    items_scraped = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Scraping job {self.id} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
