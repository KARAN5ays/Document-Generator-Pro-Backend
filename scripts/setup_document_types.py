
import os
import django
import sys

# Add the project directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DocumentGenerator.settings')
django.setup()

from backendapp.models import DocumentType

def setup_types():
    # Read the template content
    template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backendapp', 'templates', 'backendapp', 'document.html')
    with open(template_path, 'r') as f:
        template_html = f.read()

    types = [
        {
            "name": "Certificate",
            "fields_schema": [
                {"id": "name", "label": "Recipient Name", "type": "text", "required": True, "placeholder": "e.g. John Doe"},
                {"id": "courseName", "label": "Course Name", "type": "text", "required": True, "placeholder": "e.g. Advanced Python"},
                {"id": "grade", "label": "Grade", "type": "text", "required": False, "placeholder": "e.g. A+"},
                {"id": "date", "label": "Issue Date", "type": "date", "required": True}
            ]
        },
        {
            "name": "Receipt",
            "fields_schema": [
                {"id": "recipient", "label": "Payer Name", "type": "text", "required": True},
                {"id": "amount", "label": "Amount ($)", "type": "number", "required": True},
                {"id": "payment_method", "label": "Payment Method", "type": "text", "required": True, "placeholder": "e.g. Credit Card, Cash"},
                {"id": "description", "label": "Description", "type": "textarea", "required": True},
                {"id": "date", "label": "Date", "type": "date", "required": True}
            ]
        },
        {
            "name": "Letter",
            "fields_schema": [
                {"id": "recipient_name", "label": "Recipient Name", "type": "text", "required": True},
                {"id": "recipient_address", "label": "Recipient Address", "type": "textarea", "required": True},
                {"id": "subject", "label": "Subject", "type": "text", "required": True},
                {"id": "body", "label": "Letter Body", "type": "textarea", "required": True},
                {"id": "sender_name", "label": "Sender Name", "type": "text", "required": True},
                {"id": "sender_role", "label": "Sender Role/Title", "type": "text", "required": True},
                {"id": "sender_address", "label": "Sender Address", "type": "textarea", "required": False},
                {"id": "date", "label": "Date", "type": "date", "required": True}
            ]
        },
        {
            "name": "ID Card",
            "fields_schema": [
                {"id": "full_name", "label": "Full Name", "type": "text", "required": True},
                {"id": "role", "label": "Role / Title", "type": "text", "required": True},
                {"id": "department", "label": "Department", "type": "text", "required": True},
                {"id": "employee_id", "label": "Employee ID", "type": "text", "required": True},
                {"id": "expiry_date", "label": "Expiry Date", "type": "date", "required": True}
            ]
        },
        {
            "name": "Ticket",
            "fields_schema": [
                {"id": "event_name", "label": "Event Name", "type": "text", "required": True},
                {"id": "ticket_type", "label": "Ticket Type", "type": "text", "required": True, "placeholder": "e.g. VIP, General"},
                {"id": "date", "label": "Date", "type": "date", "required": True},
                {"id": "time", "label": "Time", "type": "time", "required": True},
                {"id": "venue", "label": "Venue", "type": "text", "required": True},
                {"id": "price", "label": "Price", "type": "number", "required": True},
                {"id": "seat", "label": "Seat Number", "type": "text", "required": False}
            ]
        }
    ]

    for t in types:
        obj, created = DocumentType.objects.update_or_create(
            name=t["name"],
            defaults={
                "template_html": template_html,
                "fields_schema": t["fields_schema"]
            }
        )
        action = "Created" if created else "Updated"
        print(f"{action} DocumentType: {t['name']}")

if __name__ == "__main__":
    setup_types()
