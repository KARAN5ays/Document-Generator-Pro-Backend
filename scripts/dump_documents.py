"""
Dump documents from the database to JSON using Django ORM.
Usage: python manage.py shell < scripts/dump_documents.py
Or: python scripts/dump_documents.py (run from project root with DJANGO_SETTINGS_MODULE set)
"""
import json
import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DocumentGenerator.settings")

import django
django.setup()

from backendapp.models import Document


def dump_documents(output_path="document_dump.json"):
    """Export all documents to a JSON file."""
    documents = list(
        Document.objects.values(
            "id", "tracking_field", "metadata", "status", "created_at"
        )
    )
    with open(output_path, "w") as f:
        json.dump(documents, f, indent=2)
    print(f"Successfully dumped {len(documents)} documents to {output_path}")


if __name__ == "__main__":
    dump_documents()
