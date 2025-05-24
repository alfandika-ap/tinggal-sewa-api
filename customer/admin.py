from django.contrib import admin
from unfold.admin import ModelAdmin
# Register your models here.
from .models import Customer, Kost, Bookmark


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ("id", "user", "fullname", "phone", "created_at", "updated_at")
    search_fields = ("id", "user__username", "fullname", "phone", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Kost)
class KostAdmin(ModelAdmin):
    list_display = ("id", "title", "city", "province", "price", "gender", "created_at")
    search_fields = ("id", "title", "address", "city", "province", "description")
    list_filter = ("city", "province", "gender", "created_at")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Bookmark)
class BookmarkAdmin(ModelAdmin):
    list_display = ("id", "user", "kost_title", "created_at")
    search_fields = ("id", "user__username", "kost__title")
    list_filter = ("created_at", "user")
    readonly_fields = ("id", "created_at")
    
    def kost_title(self, obj):
        return obj.kost.title
    
    kost_title.short_description = "Kost"
    kost_title.admin_order_field = "kost__title"
