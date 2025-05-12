from django.contrib import admin

from .models import ChatMessages


# Register your models here.
@admin.register(ChatMessages)
class ChatMessagesAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "content", "role", "created_at", "updated_at")
    search_fields = ("id", "user__username", "created_at", "updated_at")
    list_filter = ("user", "created_at", "updated_at")
