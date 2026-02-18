from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from backendapp.models import Document, DocumentType
from backendapp.serializers import (
    DocumentCreateSerializer,
    DocumentListSerializer,
    DocumentVerifySerializer,
)
from backendapp.services.pdf_service import generate_document_pdf


class DocumentCreateView(generics.CreateAPIView):
    """
    Create a new document.
    """
    serializer_class = DocumentCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(issued_by=self.request.user)


class DocumentListView(generics.ListAPIView):
    """
    List all documents created by the current user.
    """
    serializer_class = DocumentListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.select_related('document_type').filter(issued_by=self.request.user).order_by("-created_at")


class DocumentVerifyView(APIView):
    """
    Verify a document by its tracking ID. Public access.
    """
    permission_classes = [AllowAny]

    def get(self, request, tracking_field):
        document = get_object_or_404(
            Document.objects.select_related('document_type'), 
            tracking_field=tracking_field
        )
        serializer = DocumentVerifySerializer(document)
        return Response({"document": serializer.data})


class DocumentDetailView(generics.RetrieveAPIView):
    """
    Retrieve details of a specific document.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentListSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "tracking_field"
    
    def get_queryset(self):
         # Users can only see their own documents
        return Document.objects.select_related('document_type').filter(issued_by=self.request.user)


class DocumentDownloadView(APIView):
    """
    Download the PDF for a document.
    Generates it if it doesn't exist.
    """
    permission_classes = [AllowAny]

    def get(self, request, tracking_field):
        document = get_object_or_404(Document, tracking_field=tracking_field)
        
        # Check permissions? The prompt says "Public access" for verify, maybe for download too?
        # The URL pattern is public in some apps, but let's check if the user needs to be authenticated for download.
        # Given it's a "verify" flow, usually the person verifying (who might be public/3rd party) needs to see the PDF.
        # So AllowAny seems appropriate if they have the tracking_field.
        
        if not document.pdf_url:
            # Generate PDF if missing
            # We need to construct the HTML. 
            # The model has template_html, but usually we render it with context.
            # The tests showed simplified template_html.
            # The actual generation logic might depend on how templates are stored.
            # `generate_document_pdf` takes (document, html_string).
            
            # Simplified generation logic:
            if document.document_type and document.document_type.template_html:
                 # In a real app, we'd use Django template engine or Jinja2 to render this with document.metadata
                 # For now, let's assume simple replacement or pass as is if it's already full HTML?
                 # The test example was: "<div>{{ metadata.test }}</div>"
                 # So we likely need to render it.
                 from django.template import Template, Context
                 template = Template(document.document_type.template_html)
                 context = Context({'metadata': document.metadata, 'document': document})
                 html_string = template.render(context)
                 generate_document_pdf(document, html_string)
            else:
                 return Response({"error": "No template available for this document"}, status=status.HTTP_404_NOT_FOUND)

        if not document.pdf_url:
            return Response({"error": "PDF generation failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return FileResponse(document.pdf_url.open(), as_attachment=True, filename=f"{tracking_field}.pdf")
