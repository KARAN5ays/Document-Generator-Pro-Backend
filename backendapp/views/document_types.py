"""
Document Type API views - list and create document templates.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from backendapp.models import DocumentType
from backendapp.serializers import DocumentTypeSerializer
from backendapp.permissions import IsStaffUser


class DocumentTypeListView(APIView):
    """List all document types (GET) or create a new one (POST, staff only)."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsStaffUser()]
        return [AllowAny()]

    def get(self, request):
        types = DocumentType.objects.all()
        serializer = DocumentTypeSerializer(types, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DocumentTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentTypeDetailView(APIView):
    """Retrieve, update, or delete a document type."""

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsStaffUser()]

    def get(self, request, pk):
        """Return full template data (including ui_config) for editing."""
        try:
            doc_type = DocumentType.objects.get(pk=pk)
            serializer = DocumentTypeSerializer(doc_type)
            return Response(serializer.data)
        except DocumentType.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):
        """Partially update a template (name, fields_schema, ui_config, etc.)."""
        try:
            doc_type = DocumentType.objects.get(pk=pk)
        except DocumentType.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentTypeSerializer(doc_type, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Permanently delete a document type."""
        try:
            doc_type = DocumentType.objects.get(pk=pk)
            doc_type.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DocumentType.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
