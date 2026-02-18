# Document Generator Backend

Django REST API for document generation, verification, and analytics.

## Project Structure

```
Document_Generator_backend/
├── backendapp/                 # Main application
│   ├── constants.py            # App constants (status values, roles)
│   ├── models.py               # User, Document, DocumentType
│   ├── serializers.py          # DRF serializers
│   ├── permissions.py          # Custom permission classes
│   ├── admin.py                # Django admin configuration
│   ├── views/                  # API views (split by domain)
│   │   ├── __init__.py
│   │   ├── document_types.py   # Document type CRUD
│   │   ├── documents.py        # Create & verify documents
│   │   └── analytics.py        # Dashboard analytics
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   └── pdf_service.py      # PDF generation
│   ├── templatetags/           # Template filters
│   └── templates/              # HTML templates for documents
├── DocumentGenerator/          # Project config
│   ├── settings.py
│   └── urls.py
├── scripts/
│   ├── setup_document_types.py # Seed document types
│   └── dump_documents.py       # Export documents to JSON
├── requirements.txt
├── .env.example
└── manage.py
```

## Setup

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python scripts/setup_document_types.py
python manage.py runserver
```

## Environment Variables

Copy `.env.example` to `.env` and configure for production:

- `DJANGO_SECRET_KEY` - Required in production
- `DJANGO_DEBUG` - Set to `false` in production
- `DJANGO_ALLOWED_HOSTS` - Comma-separated hosts
- `CORS_ALLOWED_ORIGINS` - Allowed frontend origins

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/document-types/` | JWT | List document types |
| POST | `/api/document-types/` | Staff | Create document type |
| POST | `/api/create/` | Staff | Create document & generate PDF |
| GET | `/api/verify/<tracking_field>/` | None | Verify document |
| GET | `/api/analytics/` | JWT | Dashboard analytics |
| POST | `/api/token/` | None | Obtain JWT |
| POST | `/api/token/refresh/` | None | Refresh JWT |
