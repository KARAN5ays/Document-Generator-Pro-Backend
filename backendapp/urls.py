from django.urls import path
from .views import (
    DocumentCreateView,
    DocumentListView,
    DocumentVerifyView,
    DocumentDownloadView,
    DocumentTypeListView,
    DashboardAnalyticsView,
    TemplateBuilderConfigView,
    VerificationStatsView,
    DocumentDetailView,
    DocumentTypeDetailView,
)
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
<<<<<<< HEAD
from backendapp.views.auth import RegisterView, UserProfileView
=======
from backendapp.views.auth import RegisterView , UserProfileView
>>>>>>> 921c41f (server commit)

urlpatterns = [
    path("document-types/", DocumentTypeListView.as_view(), name="document-type-list"),
    path("document-types/<int:pk>/", DocumentTypeDetailView.as_view(), name="document-type-detail"),
    path("create/", DocumentCreateView.as_view(), name="document-create"),
    path("documents/", DocumentListView.as_view(), name="document-list"),
    path("verification-stats/", VerificationStatsView.as_view(), name="verification-stats"),
    path("verify/<str:tracking_field>/", DocumentVerifyView.as_view(), name="document-verify"),
    path(
        "documents/<str:tracking_field>/download/",
        DocumentDownloadView.as_view(),
        name="document-download",
    ),
    path(
        "documents/<str:tracking_field>/",
        DocumentDetailView.as_view(),
        name="document-detail",
    ),
    path("analytics/", DashboardAnalyticsView.as_view(), name="dashboard-analytics"),
    path("template-builder-config/", TemplateBuilderConfigView.as_view(), name="template-builder-config"),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
<<<<<<< HEAD
    path('users/me/', UserProfileView.as_view(), name='user-profile'),
=======
    path('users/me/' , UserProfileView.as_view() , name = 'user-profile')
>>>>>>> 921c41f (server commit)
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
