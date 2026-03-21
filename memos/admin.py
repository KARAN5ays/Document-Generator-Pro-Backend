from django.contrib import admin
from memos.models import Memo


@admin.register(Memo)
class MemoAdmin(admin.ModelAdmin):
    list_display = (
        "reference_number",
        "title",
        "amount",
        "approval_status",
        "created_by",
        "merchant",
        "created_at",
    )

    search_fields = (
        "reference_number",
        "title",
        "created_by__username",
    )

    list_filter = (
        "approval_status",
        "merchant",
        "memo_type",
    )

    readonly_fields = (
        "reference_number",
        "created_by",
        "merchant",
        "approval_status",
        "approval_status_meta",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Basic Info", {
            "fields": (
                "reference_number",
                "title",
                "amount",
                "memo_type",
            ),
        }),
        ("Departments", {
            "fields": (
                "from_department",
                "to_department",
            ),
        }),
        ("Content", {
            "fields": (
                "subject",
                "purpose",
                "background",
            ),
        }),
        ("Approval Info", {
            "fields": (
                "approval_chain",
                "approval_status",
                "approval_status_meta",
            ),
        }),
        ("Ownership", {
            "fields": (
                "created_by",
                "merchant",
            ),
        }),
        ("Timestamps", {
            "fields": (
                "created_at",
                "updated_at",
            ),
        }),
    )