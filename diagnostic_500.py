import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DocumentGenerator.settings')
try:
    django.setup()
    print("Django setup successful")
except Exception as e:
    print(f"Django setup failed: {e}")
    sys.exit(1)

from backendapp.models import Document, User
from django.test import RequestFactory
from backendapp.views.documents import DocumentListView

try:
    # Test a simple query to verify select_related logic
    user = User.objects.first()
    if not user:
        print("No user found in DB")
    else:
        print(f"Testing query for user: {user.username}")
        docs = Document.objects.filter(issued_by=user).select_related('document_type', 'issued_by')[:5]
        print(f"Query successful, found {len(docs)} docs")
        
        # Test the view logic
        factory = RequestFactory()
        request = factory.get('/api/documents/')
        request.user = user
        view = DocumentListView.as_view()
        response = view(request)
        print(f"View response status: {response.status_code}")
except Exception as e:
    import traceback
    print("Diagnostic failed with error:")
    traceback.print_exc()
