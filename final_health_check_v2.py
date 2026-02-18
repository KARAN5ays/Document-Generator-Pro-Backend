import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DocumentGenerator.settings')
django.setup()

from backendapp.models import Document, User, DocumentType
from django.conf import settings
try:
    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
except ImportError:
    OutstandingToken = None

def health_check():
    print("--- START ENHANCED HEALTH CHECK ---")
    
    # 1. User & Document Consistency
    print("Users and their Document Counts:")
    for user in User.objects.all():
        doc_count = Document.objects.filter(issued_by=user).count()
        print(f"  User: {user.username} (ID: {user.id}), Docs Issued: {doc_count}")
        if user.username == 'luffy' and doc_count != 18:
             print(f"  WARNING: Expected 18 docs for luffy, found {doc_count}")

    # 2. Total across all users
    total_db_count = Document.objects.count()
    print(f"TOTAL_DOCS_IN_DB: {total_db_count}")
    
    # 3. Storage Check
    media_path = os.path.join(settings.MEDIA_ROOT, 'documents')
    if os.path.exists(media_path):
        files = [f for f in os.listdir(media_path) if f.endswith('.pdf')]
        print(f"PDF_FILES_ON_DISK: {len(files)}")
        # Check if every document in DB has a file
        for doc in Document.objects.all():
            if doc.pdf_url:
                full_path = os.path.join(settings.BASE_DIR, str(doc.pdf_url))
                if not os.path.exists(full_path):
                    print(f"  MISSING FILE: Doc {doc.tracking_field} expects {full_path}")
    else:
        print("MEDIA_DOCS_FOLDER_MISSING")

    # 4. Token Storage Check
    if OutstandingToken:
        token_count = OutstandingToken.objects.count()
        print(f"OUTSTANDING_TOKENS_IN_DB: {token_count}")
    else:
        print("TOKEN_BLACKLIST_MODEL_NOT_FOUND")

    # 5. Check "karan" template status
    karan_template = DocumentType.objects.filter(name__iexact="karan").first()
    print(f"KARAN_TEMPLATE_EXISTS: {'YES' if karan_template else 'NO'}")

    print("--- END ENHANCED HEALTH CHECK ---")

if __name__ == "__main__":
    health_check()
