from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        STAFF = 'STAFF', 'Staff'

    # Legacy field for Document Generator
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STAFF)
    
    # New fields for Memo Approval System
    idx = models.CharField(max_length=20 , unique=True , editable=False , db_index=True , null=True)
    display_name = models.CharField(max_length=255, blank=True)
    merchant = models.ForeignKey('autho.Merchant', on_delete=models.PROTECT, related_name='users', null=True, blank=True)
    roles = models.ManyToManyField('permission.Role', blank=True, related_name='users')

    class Meta:
        db_table = 'documentapp_user'

    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    is_staff = models.BooleanField(default=True, help_text="Designates whether the user can create documents.")


    def save(self, *args, **kwargs):
        """ On save, generate a unique idx if not already set. """
        if not self.idx:
            import uuid
            self.idx = uuid.uuid4().hex[:20].upper()  # Generate a unique 20-character ID
        super().save(*args, **kwargs)
    
    def iss(self, role_names):
        """ Check if the user has specific roles in the Memo Approval System. """
        if isinstance(role_names, str):
            role_names = [role_names]
        return self.roles.filter(name__in=role_names).exists()

    def __str__(self):
        name = self.display_name or self.username or self.email or str(self.id)
        if self.merchant:
            return f"{name} ({self.merchant.name})"
        return name


class Template(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="Name of the document type (e.g., certificate, receipt)")
    template_html = models.TextField(help_text="HTML template for the document type", blank=True, null=True)
    template_file = models.CharField(max_length=255, help_text="Path to the template file (e.g. documentapp/custom_templates/my_template.html)", blank=True, null=True)
    fields_schema = models.JSONField(default=list, help_text="JSON list of field definitions for this template")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='templates', null=True, blank=True, help_text="User who created this template. Null means global system template.")

    class Meta:
        db_table = 'documentapp_template'


    def __str__(self):
        return self.name
    

class Document(models.Model):
    document_type = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='documents', null=True)
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

    class Meta:
        db_table = 'documentapp_document'


    def __str__(self):
        return f"{self.document_type.name if self.document_type else 'Unknown'} - {self.tracking_field}"


class CompanyAsset(models.Model):
    class AssetType(models.TextChoices):
        LOGO = 'logo', 'Logo'
        SIGNATURE = 'signature', 'Signature'
        STAMP = 'stamp', 'Stamp'

    name = models.CharField(max_length=100, help_text="Human-readable label, e.g. 'Main Logo'")
    file = models.ImageField(upload_to='assets/', help_text="The uploaded image file")
    asset_type = models.CharField(max_length=20, choices=AssetType.choices, default=AssetType.LOGO)
    is_default = models.BooleanField(default=False, help_text="Mark as the default asset for its type")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assets')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documentapp_companyasset'


    def __str__(self):
        return f"{self.get_asset_type_display()} – {self.name}"

    def save(self, *args, **kwargs):
        # If this asset is being set as default, unset others of the same type for this user
        if self.is_default:
            CompanyAsset.objects.filter(
                uploaded_by=self.uploaded_by,
                asset_type=self.asset_type,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
