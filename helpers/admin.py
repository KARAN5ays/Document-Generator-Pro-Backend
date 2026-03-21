from django.contrib import admin


class BaseModelAdmin(admin.ModelAdmin):
    """Base admin class that sets common read-only fields for all BaseModel-derived models."""
    readonly_fields = ("idx", "created_at", "updated_at")


class BaseReadOnlyModelAdmin(BaseModelAdmin):
    """Admin class where ALL fields are read-only (useful for log/audit models)."""

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
