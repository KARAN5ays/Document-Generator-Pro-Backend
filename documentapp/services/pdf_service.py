"""
PDF generation service with error handling.
"""

import logging

from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


def generate_document_pdf(document, html_string):
    """
    Generate a PDF from HTML and attach it to the document.

    Args:
        document: Document model instance
        html_string: Rendered HTML content

    Returns:
        FileField: The saved pdf_url field

    Raises:
        ValueError: If PDF generation fails
    """
    try:
        from weasyprint import HTML  # lazy import — avoids crashing views on startup if WeasyPrint is missing
        pdf_bytes = HTML(string=html_string).write_pdf()
    except ImportError:
        raise ValueError("WeasyPrint is not installed. Please run: pip install WeasyPrint")
    except Exception as e:
        logger.exception(
            "Failed to generate PDF for document %s: %s", document.pk, str(e)
        )
        raise ValueError(f"PDF generation failed: {str(e)}") from e

    filename = f"{document.tracking_field}.pdf"
    document.pdf_url.save(filename, ContentFile(pdf_bytes), save=True)
    return document.pdf_url
