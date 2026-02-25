from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from backendapp.models import CompanyAsset
from backendapp.serializers import CompanyAssetSerializer


class AssetListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/assets/        — List all assets for the current user
    POST /api/assets/        — Upload a new asset (multipart/form-data)
    """
    serializer_class = CompanyAssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = CompanyAsset.objects.filter(uploaded_by=self.request.user).order_by('-created_at')
        asset_type = self.request.query_params.get('type')
        if asset_type:
            qs = qs.filter(asset_type=asset_type)
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class AssetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/assets/<pk>/  — Retrieve an asset
    PATCH  /api/assets/<pk>/  — Update name / is_default flag
    DELETE /api/assets/<pk>/  — Delete an asset (also removes the file)
    """
    serializer_class = CompanyAssetSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return CompanyAsset.objects.filter(uploaded_by=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_destroy(self, instance):
        # Delete the actual file from storage before removing the DB record
        if instance.file:
            try:
                instance.file.delete(save=False)
            except Exception:
                pass
        instance.delete()
