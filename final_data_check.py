import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DocumentGenerator.settings')
django.setup()

from backendapp.models import Document, User
from django.conf import settings

def final_test():
    print("--- FINAL DATA INTEGRITY CHECK ---")
    
    # Check luffy user specifically
    luffy = User.objects.get(username='luffy')
    docs = Document.objects.filter(issued_by=luffy).order_by('-created_at')
    print(f"Luffy (ID: {luffy.id}) has {docs.count()} documents.")
    
    if docs.exists():
        last_doc = docs[0]
        print(f"Latest Doc for Luffy: {last_doc.tracking_field}")
        print(f"  - Metadata Keys: {list(last_doc.metadata.keys())}")
        print(f"  - PDF URL: {last_doc.pdf_url}")
        
        # Verify physical file existence
        # pdf_url is e.g. 'documents/8ED00626.pdf'
        # MEDIA_ROOT is '.../media'
        if last_doc.pdf_url:
            physical_path = os.path.join(settings.MEDIA_ROOT, str(last_doc.pdf_url))
            print(f"  - Expected physical path: {physical_path}")
            if os.path.exists(physical_path):
                print("  - FILE EXISTS ON DISK: YES")
            else:
                print("  - FILE EXISTS ON DISK: NO")
    
    # Check Storage structure
    media_docs_dir = os.path.join(settings.MEDIA_ROOT, 'documents')
    print(f"\nMedia Documents Directory: {media_docs_dir}")
    if os.path.exists(media_docs_dir):
        files = os.listdir(media_docs_dir)
        print(f"Total PDF files in folder: {len([f for f in files if f.endswith('.pdf')])}")
    
    print("\n--- TEST COMPLETE ---")

if __name__ == "__main__":
    final_test()
