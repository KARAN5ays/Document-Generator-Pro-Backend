from django.contrib import admin
from .models import Document, DocumentType, User, CompanyAsset


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active")
    search_fields = ("username", "email")


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
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
