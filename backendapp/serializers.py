from rest_framework import serializers
from .models import User, Document, DocumentType
import uuid

class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ['id', 'name', 'template_html', 'template_file', 'fields_schema', 'ui_config']
        extra_kwargs = {
            'template_html': {'required': False},
            'template_file': {'required': False},
        }

    def validate(self, data):
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

