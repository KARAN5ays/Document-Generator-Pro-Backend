from django.contrib import admin
from .models import Merchant


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ("idx", "name", "email", "is_active", "created_at")
    search_fields = ("name", "email")
    list_filter = ("is_active",)
    readonly_fields = ("idx", "created_at", "updated_at")