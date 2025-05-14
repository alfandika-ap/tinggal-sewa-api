from django.db import models

from core.utils import generate_id


class BaseModel(models.Model):
    id = models.CharField(
        primary_key=True, max_length=100, default=generate_id, editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

clas Page(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    keyword = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or self.url

class Image(models.Model):
    page = models.ForeignKey(Page, related_name='images', on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to='images/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image_file.url