from django.contrib import admin

# Register your models here.
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at')
    search_fields = ('id', 'user__username', 'created_at', 'updated_at')
    list_filter = ('user', 'created_at', 'updated_at')