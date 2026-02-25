from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        STAFF = 'STAFF', 'Staff'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STAFF)
    username = models.CharField(max_length=150, unique=True , null=True , blank=True)
    email = models.EmailField(unique=True , null=True , blank=True)
    is_staff = models.BooleanField(default=True, help_text="Designates whether the user can create documents.")
    
    def __str__(self):
        return self.username or self.email or str(self.id)


class DocumentType(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="Name of the document type (e.g., certificate, receipt)")
    template_html = models.TextField(help_text="HTML template for the document type", blank=True, null=True)
    template_file = models.CharField(max_length=255, help_text="Path to the template file (e.g. backendapp/custom_templates/my_template.html)", blank=True, null=True)
    fields_schema = models.JSONField(default=list, help_text="JSON list of field definitions for this template")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='templates', null=True, blank=True, help_text="User who created this template. Null means global system template.")

    def __str__(self):
        return self.name
    

class Document(models.Model):
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, related_name='documents', null=True)
    tracking_field = models.CharField(max_length=50, unique=True, help_text="Unique verification code",db_index=True , validators=[MinLengthValidator(8),RegexValidator(r'^[A-Z0-9]+$')])
    metadata = models.JSONField(help_text="Flexible object for document data")
    pdf_url = models.FileField(upload_to='documents/', blank=True, null=True)
    status = models.CharField(
        max_length=20,
        default="valid",
        choices=[("valid", "Valid"), ("revoked", "Revoked")],
        help_text="Status of the document (valid/revoked)",
    )
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_type.name if self.document_type else 'Unknown'} - {self.tracking_field}"
