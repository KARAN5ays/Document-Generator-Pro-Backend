"""
Template Builder configuration. Edit this file to change template builder behavior
without touching the frontend. All options are served via API.
"""

# Field types available when creating templates (editable from backend)
FIELD_TYPES = [
    {"value": "text", "label": "Text", "description": "Single-line text input"},
    {"value": "textarea", "label": "Text Area", "description": "Multi-line text for longer content"},
    {"value": "number", "label": "Number", "description": "Numeric values"},
    {"value": "date", "label": "Date", "description": "Date picker"},
    {"value": "time", "label": "Time", "description": "Time picker"},
    {"value": "email", "label": "Email", "description": "Email address"},
    {"value": "url", "label": "URL", "description": "Web link"},
]

# Layout options for templates
LAYOUT_OPTIONS = [
    {"value": "standard", "label": "Standard", "description": "Default document layout"},
    {"value": "certificate", "label": "Certificate", "description": "Centered certificate style"},
    {"value": "receipt", "label": "Receipt", "description": "Compact receipt/invoice layout"},
    {"value": "idcard", "label": "ID Card", "description": "Card-style compact layout"},
    {"value": "letter", "label": "Letter", "description": "Formal letter format"},
]

# Default HTML template for Code Mode (editable from backend)
DEFAULT_HTML_TEMPLATE = """<div class="layout-custom" style="padding: 40px; font-family: sans-serif;">
  <h1 style="color: #1e293b;">{{ document.template_type }}</h1>
  <div style="margin-top: 20px;">
    <p><strong>Name:</strong> {{ metadata.name }}</p>
    <p><strong>Date:</strong> {{ metadata.date }}</p>
    <!-- Add more fields: {{ metadata.your_field_id }} -->
  </div>
  <div style="margin-top: 40px; font-size: 12px; color: #94a3b8;">
    ID: {{ document.tracking_field }}
  </div>
</div>"""

# UI copy and help text (editable from backend)
HELP_TEXTS = {
    "template_name_placeholder": "e.g. Event Ticket, Invoice, Certificate...",
    "template_name_help": "Choose a unique name. This appears when creating documents.",
    "field_label_help": "Shown to users when filling the form.",
    "field_id_help": "Used in templates as {{ metadata.field_id }}. Use lowercase with underscores.",
    "ui_mode_description": "Define fields visually. Great for certificates, receipts, and simple documents.",
    "code_mode_description": "Write custom HTML. Use {{ metadata.field_id }} for dynamic content.",
}

# Base template file path for UI mode (editable from backend)
DEFAULT_TEMPLATE_FILE = "backendapp/base_universal_template.html"


def get_template_builder_config():
    """Return full config for the template builder frontend."""
    return {
        "field_types": FIELD_TYPES,
        "layout_options": LAYOUT_OPTIONS,
        "default_html": DEFAULT_HTML_TEMPLATE,
        "help_texts": HELP_TEXTS,
        "default_template_file": DEFAULT_TEMPLATE_FILE,
    }
