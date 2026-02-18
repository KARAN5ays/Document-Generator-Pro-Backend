import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DocumentGenerator.settings')
django.setup()

from backendapp.models import Document, User
from django.conf import settings

def health_check():
    print("--- START HEALTH CHECK ---")
    
    # 1. Document Count
    luffy = User.objects.get(username='luffy')
    luffy_count = Document.objects.filter(issued_by=luffy).count()
    total_count = Document.objects.count()
    print(f"LUFFY_DOC_COUNT: {luffy_count}")
    print(f"TOTAL_DOC_COUNT: {total_count}")
    
    # 2. Storage Check
    media_path = os.path.join(settings.MEDIA_ROOT, 'documents')
    if os.path.exists(media_path):
        files = [f for f in os.listdir(media_path) if f.endswith('.pdf')]
        print(f"PDF_FILES_ON_DISK: {len(files)}")
    else:
        print("MEDIA_DOCS_FOLDER_MISSING")

    # 3. Token Configuration
    jwt_config = getattr(settings, 'SIMPLE_JWT', {})
    print(f"JWT_STATELESS: {'YES' if 'BLACKLIST_AFTER_ROTATION' not in jwt_config else 'NO (Blacklist enabled)'}")
    
    print("--- END HEALTH CHECK ---")

if __name__ == "__main__":
    health_check()
