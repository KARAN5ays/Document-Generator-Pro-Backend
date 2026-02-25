from rest_framework import serializers
from .models import User, Document, DocumentType, CompanyAsset
import uuid

class DocumentTypeSerializer(serializers.ModelSerializer):
    can_edit_in_builder = serializers.SerializerMethodField()

    class Meta:
        model = DocumentType
        fields = ['id', 'name', 'template_html', 'template_file', 'fields_schema', 'can_edit_in_builder']
        extra_kwargs = {
            'template_html': {'required': False},
            'template_file': {'required': False},
        }

    def get_can_edit_in_builder(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.created_by == request.user
        return False

    def validate(self, data):
        # On partial updates (PATCH), skip this check — the existing instance
        # already has whatever template source it needs.
        if self.partial:
            return data
        if not data.get('template_html') and not data.get('template_file'):
            raise serializers.ValidationError("Either 'template_html' or 'template_file' must be provided.")
        return data

class DocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['document_type', 'tracking_field' ,'metadata']
        read_only_fields = ['status', 'tracking_field']

    def create(self , validated_data):
        validated_data['tracking_field'] = str(uuid.uuid4())[:8].upper()
        return Document.objects.create(**validated_data)

class DocumentVerifySerializer(serializers.ModelSerializer):
    template_type = serializers.CharField(source='document_type.name', read_only=True)
    class Meta:
        model = Document
        fields = ['tracking_field', 'template_type' , 'metadata' , 'created_at' , 'status']
        read_only_fields = ['tracking_field', 'template_type' , 'metadata' , 'created_at' , 'status']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class DocumentListSerializer(serializers.ModelSerializer):
    """Serializer for listing user's documents."""
    document_type_name = serializers.CharField(source='document_type.name', read_only=True)
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'tracking_field', 'document_type_name', 'metadata', 'status', 'created_at', 'pdf_url']

    def get_pdf_url(self, obj):
        if obj.pdf_url:
            return obj.pdf_url.url
        return None


class CompanyAssetSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = CompanyAsset
        fields = ['id', 'name', 'file', 'file_url', 'asset_type', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at', 'file_url']
        extra_kwargs = {'file': {'write_only': True}}

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
