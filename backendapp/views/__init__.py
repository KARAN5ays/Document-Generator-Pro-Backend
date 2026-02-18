"""
Views package - exports all API view classes for URL configuration.
"""

from .document_types import DocumentTypeListView, DocumentTypeDetailView
from .analytics import DashboardAnalyticsView, VerificationStatsView
from .template_config import TemplateBuilderConfigView
from .documents import (
    DocumentCreateView,
    DocumentListView,
    DocumentVerifyView,
    DocumentDownloadView,
    DocumentDetailView,
)

__all__ = [
    "DocumentTypeListView",
    "DocumentTypeDetailView",
    "DashboardAnalyticsView",
    "VerificationStatsView",
    "TemplateBuilderConfigView",
    "DocumentCreateView",
    "DocumentListView",
    "DocumentVerifyView",
    "DocumentDownloadView",
    "DocumentDetailView",
]
