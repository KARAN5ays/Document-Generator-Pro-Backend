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
from .assets import AssetListCreateView, AssetDetailView
from .bulk_issuance import BulkIssuanceView

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
    "AssetListCreateView",
    "AssetDetailView",
    "BulkIssuanceView",
]
