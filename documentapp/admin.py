from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import Document, Template, User, CompanyAsset


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Memo System", {"fields": ("idx", "display_name", "merchant", "roles", "role")}),
    )
    list_display = ("username", "email", "display_name", "merchant", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "merchant", "is_staff", "is_superuser")
    search_fields = ("username", "email", "display_name")
    filter_horizontal = ("roles",)
    readonly_fields = ("idx",)


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "created_documents_count")
    search_fields = ("name",)

    def created_documents_count(self, obj):
        return obj.documents.count()

    created_documents_count.short_description = "Documents"


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("tracking_field", "document_type", "status", "issued_by", "created_at")
    list_filter = ("status", "document_type")
    search_fields = ("tracking_field",)
    readonly_fields = ("tracking_field", "created_at")
    date_hierarchy = "created_at"


@admin.register(CompanyAsset)
class CompanyAssetAdmin(admin.ModelAdmin):
    list_display = ("name", "asset_type", "is_default", "uploaded_by", "created_at")
    list_filter = ("asset_type", "is_default")
    search_fields = ("name",)
    readonly_fields = ("created_at",)
