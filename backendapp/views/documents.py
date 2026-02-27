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


class DocumentDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete a specific document  """
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
        
        # Option to force-regenerate PDF (useful if template or data changed)
        force_regenerate = request.query_params.get('force', 'false').lower() == 'true'
        
        if not document.pdf_url or force_regenerate:
            from django.template.loader import render_to_string
            from django.template import Template, Context
            import re

            # Prepare context for rendering
            # Include metadata items for compatibility with system templates
            metadata = document.metadata or {}
            metadata_items = []
            if isinstance(metadata, dict):
                metadata_items = list(metadata.items())

            context_dict = {
                'document': document,
                'metadata': metadata,
                'metadata_items': metadata_items,
                'unique_code': document.tracking_field,
                'tracking_code': document.tracking_field,
                **metadata, # Unpack so {{ Name }} works directly
            }

            if document.document_type and document.document_type.template_html:
                # 1. CLEAN TEMPLATE: CKEditor might add &nbsp; or other tags inside {{ ... }}
                raw_html = document.document_type.template_html
                # Replace &nbsp; with space inside curly braces to help Django parser
                # Simple heuristic: find sequences between {{ and }} and clean them
                def clean_vars(match):
                    return match.group(0).replace('&nbsp;', ' ').replace('&#160;', ' ')
                
                cleaned_html = re.sub(r'\{\{.*?\}\}', clean_vars, raw_html)
                
                try:
                    template = Template(cleaned_html)
                    context = Context(context_dict)
                    content_html = template.render(context)
                except Exception as e:
                    logger.error(f"Template rendering failed: {e}")
                    content_html = raw_html # Fallback to raw

                # 2. WRAP IN SKELETON: Add basic CSS so it looks like a document
                if '<html' not in content_html.lower():
                    html_string = f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            @page {{ size: A4; margin: 20mm; }}
                            body {{ 
                                font-family: 'Helvetica', 'Arial', sans-serif; 
                                color: #1e293b; 
                                line-height: 1.6; 
                                margin: 0; 
                                padding: 0;
                            }}
                            .ck-content {{ font-size: 14px; min-height: 230mm; }}
                            /* Mimic some CKEditor styles */
                            blockquote {{ border-left: 4px solid #db2777; background: #fdf2f8; padding: 1rem; margin: 1rem 0; font-style: italic; }}
                            table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
                            table td, table th {{ border: 1px solid #e2e8f0; padding: 8px; }}
                            .header {{
                                text-align: right;
                                margin-bottom: 5mm;
                                font-family: monospace;
                                font-size: 10px;
                                color: #94a3b8;
                            }}
                            .footer {{ 
                                margin-top: 10mm; 
                                padding-top: 5mm; 
                                border-top: 1px dashed #e2e8f0; 
                                text-align: center; 
                                color: #94a3b8; 
                                font-size: 10px;
                                font-family: monospace;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="header">
                            ID: {document.tracking_field}
                        </div>
                        <div class="ck-content">
                            {content_html}
                        </div>
                        <div class="footer">
                            Verification: {document.tracking_field} | Verified Authentic
                        </div>
                    </body>
                    </html>
                    """
                else:
                    html_string = content_html
            else:
                # Fallback to system template file
                template_name = getattr(document.document_type, 'template_file', None) or 'backendapp/document.html'
                try:
                    html_string = render_to_string(template_name, context_dict)
                except Exception as e:
                    logger.error(f"System template rendering failed: {e}")
                    html_string = f"<h1>Document</h1><p>Error rendering template: {e}</p>"

            try:
                generate_document_pdf(document, html_string)
            except Exception as e:
                return Response({"error": f"PDF generation failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not document.pdf_url:
            return Response({"error": "PDF file not found"}, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(document.pdf_url.open(), as_attachment=True, filename=f"{tracking_field}.pdf")
