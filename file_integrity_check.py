import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DocumentGenerator.settings')
django.setup()

from backendapp.models import Document, User
from django.conf import settings

def check_files():
    print("--- PDF FILE PATH VERIFICATION ---")
    docs_with_files = Document.objects.exclude(pdf_url='')
    print(f"Total documents with pdf_url in DB: {docs_with_files.count()}")
    
    missing_count = 0
    valid_count = 0
    
    for doc in docs_with_files:
        # FileField stores path relative to MEDIA_ROOT
        physical_path = os.path.join(settings.MEDIA_ROOT, str(doc.pdf_url))
        if os.path.exists(physical_path):
            valid_count += 1
        else:
            missing_count += 1
            if missing_count < 5:
                print(f"  MISSING: {doc.tracking_field} -> {physical_path}")
    
    print(f"\nSummary:")
    print(f"  Valid files on disk: {valid_count}")
    print(f"  Missing files on disk: {missing_count}")
    
    # Check if files exist in the folder but are not linked
    all_files = []
    media_docs_dir = os.path.join(settings.MEDIA_ROOT, 'documents')
    if os.path.exists(media_docs_dir):
        all_files = [f for f in os.listdir(media_docs_dir) if f.endswith('.pdf')]
        print(f"  Total PDF files in media/documents/: {len(all_files)}")

    print("\n--- AUTH TOKEN STORAGE CHECK ---")
    try:
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
        print(f"  Outstanding tokens in DB: {OutstandingToken.objects.count()}")
    except:
        print("  Token Blacklist not found or not configured.")

    print("\n--- END CHECK ---")

if __name__ == "__main__":
    check_files()
