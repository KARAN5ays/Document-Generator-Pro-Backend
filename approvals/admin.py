from django.contrib import admin
from helpers.admin import BaseModelAdmin, BaseReadOnlyModelAdmin
from approvals.models import ApprovalChain, ApprovalChainAction, ApprovalChainLog


@admin.register(ApprovalChain)
class ApprovalChainAdmin(BaseModelAdmin):
    list_display = ("title", "merchant", "ttl", "is_obsolete")
    search_fields = ("title",)
    list_filter = ("merchant", "is_obsolete")

    fieldsets = (
        (None, {
            "fields": ("idx", "merchant", "title", "conditions", "ttl"),
        }),
        ("Extra Information", {
            "fields": ("is_obsolete",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )


@admin.register(ApprovalChainAction)
class ApprovalChainActionAdmin(BaseModelAdmin):
    list_display = ("title", "approval_chain", "is_first", "next_action", "ttl")
    search_fields = ("title",)
    list_filter = ("approval_chain", "is_first")
    filter_horizontal = ("allowed_roles", "allowed_actors")

    fieldsets = (
        (None, {
            "fields": (
                "idx",
                "title",
                "approval_chain",
                "allowed_roles",
                "allowed_actors",
                "is_first",
                "next_action",
                "ttl",
            ),
        }),
        ("Extra Information", {
            "fields": ("is_obsolete",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )


@admin.register(ApprovalChainLog)
class ApprovalChainLogAdmin(BaseReadOnlyModelAdmin):
    list_display = ("approval_chain", "approval_action", "actor", "created_at")
    search_fields = ("actor__email",)
    list_filter = ("merchant", "approval_chain", "approval_action")

    fieldsets = (
        (None, {
            "fields": (
                "idx",
                "merchant",
                "approval_chain",
                "approval_action",
                "app_label",
                "model",
                "obj_idx",
                "actor",
                "remarks",
                "next_approval_action",
                "previous_log_in_chain",
            ),
        }),
        ("Extra Information", {
            "fields": ("is_obsolete",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )