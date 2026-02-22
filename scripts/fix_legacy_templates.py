import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DocumentGenerator.settings')
django.setup()

from backendapp.models import DocumentType, User, Document

SYSTEM_TEMPLATE_NAMES = ["Certificate", "Receipt", "Letter", "ID Card", "Ticket"]

def fix_legacy_templates():
    # Identify legacy custom templates (not in the system list, but created_by is null)
    legacy_templates = DocumentType.objects.filter(
        created_by__isnull=True
    ).exclude(
        name__in=SYSTEM_TEMPLATE_NAMES
    )
    
    count = legacy_templates.count()
    if count == 0:
        print("No legacy orphaned templates found.")
        return

    admin_fallback = User.objects.filter(is_superuser=True).first()
    if not admin_fallback:
        admin_fallback = User.objects.order_by('id').first()

    for template in legacy_templates:
        # Check if any documents were created using this template
        first_doc = Document.objects.filter(document_type=template).order_by('created_at').first()
        
        assigned_user = None
        if first_doc and first_doc.issued_by:
            assigned_user = first_doc.issued_by
            print(f"  - Reassigning '{template.name}' to user '{assigned_user.username or assigned_user.email}' (Based on document history)")
        elif admin_fallback:
            assigned_user = admin_fallback
            print(f"  - Reassigning '{template.name}' to fallback admin '{assigned_user.username or assigned_user.email}' (No document history found)")
        else:
            print(f"  - Could not reassign '{template.name}': No users exist in the database.")
            continue
            
        template.created_by = assigned_user
        template.save()
        
    print(f"Successfully processed {count} legacy custom templates.")

if __name__ == "__main__":
    fix_legacy_templates()
