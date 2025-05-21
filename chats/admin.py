from django.contrib import admin
from django.db.models import Sum
from django.utils.formats import number_format
from unfold.admin import ModelAdmin
from .models import ChatMessages


# Register your models here.
@admin.register(ChatMessages)
class ChatMessagesAdmin(ModelAdmin):
    list_display = ("id", "user", "content", "role", "token_usage_display", "function_name", "created_at", "updated_at")
    search_fields = ("id", "user__username", "token_usage", "created_at", "updated_at")
    list_filter = ("user", "created_at", "updated_at")
    
    def token_usage_display(self, obj):
        """Display token usage with formatting"""
        return number_format(obj.token_usage)
    token_usage_display.short_description = "Token Usage"
    token_usage_display.admin_order_field = "token_usage"
    
    def changelist_view(self, request, extra_context=None):
        """Add token usage summary to the changelist view"""
        extra_context = extra_context or {}
        
        # Get filtered queryset based on request
        cl = self.get_changelist_instance(request)
        queryset = cl.get_queryset(request)
        
        # Calculate total token usage for the filtered queryset
        token_summary = queryset.aggregate(total=Sum('token_usage'))
        total_usage = token_summary['total'] or 0
        
        # Format the number with commas for better readability
        extra_context['token_usage_summary'] = number_format(total_usage)
        
        return super().changelist_view(request, extra_context=extra_context)
