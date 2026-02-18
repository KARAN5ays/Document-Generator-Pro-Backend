from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import DocumentType, User

class DocumentTypeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.staff_user = User.objects.create_user(username='staffuser', email='staff@example.com', password='testpassword', is_staff=True)

    def test_create_document_type(self):
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('document-type-list')
        data = {
            "name": "New Type",
            "template_html": "<div>{{ metadata.test }}</div>",
            "fields_schema": [{"id": "test", "label": "Test", "type": "text"}]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DocumentType.objects.count(), 1)
        self.assertEqual(DocumentType.objects.get().name, "New Type")

    def test_create_document_type_permission_denied(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('document-type-list')
        data = {
             "name": "New Type Denied",
             "template_html": "<div></div>",
             "fields_schema": []
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
