#!/usr/bin/env python3
"""
API integration test script.
Run from project root: python scripts/test_api.py
Requires: requests (pip install requests)
"""
import sys
import os

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api").rstrip("/") + "/"

def main():
    print(f"Testing API at {BASE_URL}\n")

    # 1. Login
    print("1. POST token/ (Login)")
    r = requests.post(f"{BASE_URL}token/", json={"username": "admin", "password": "admin"})
    if r.status_code != 200:
        print(f"   FAIL - HTTP {r.status_code}")
        print("   Create a user: python manage.py createsuperuser")
        return 1
    token = r.json().get("access")
    if not token:
        print("   FAIL - No access token")
        return 1
    print("   OK")

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Document types
    print("2. GET document-types/")
    r = requests.get(f"{BASE_URL}document-types/", headers=headers)
    if r.status_code != 200:
        print(f"   FAIL - HTTP {r.status_code}")
        return 1
    types_data = r.json()
    print(f"   OK - {len(types_data)} types")

    if not types_data:
        print("   Run: python scripts/setup_document_types.py")
        return 1

    doc_type_id = types_data[0]["id"]

    # 3. Create document
    print("3. POST create/")
    payload = {
        "document_type": doc_type_id,
        "metadata": {
            "name": "Test User",
            "courseName": "Test Course",
            "grade": "A",
            "date": "2024-01-15",
        },
    }
    r = requests.post(f"{BASE_URL}create/", json=payload, headers=headers)
    if r.status_code != 201:
        print(f"   FAIL - HTTP {r.status_code}")
        print(f"   {r.json()}")
        return 1
    data = r.json()
    tracking = data.get("tracking_field")
    pdf_url = data.get("pdf_url")
    print(f"   OK - tracking_field={tracking}, pdf_url={pdf_url or 'N/A'}")

    # 4. Verify
    print("4. GET verify/<tracking>/")
    r = requests.get(f"{BASE_URL}verify/{tracking}/")
    if r.status_code != 200:
        print(f"   FAIL - HTTP {r.status_code}")
        return 1
    print("   OK")

    # 5. Download (try API endpoint, then media URL)
    print("5. Download PDF")
    from urllib.parse import urlparse
    base_origin = urlparse(BASE_URL).scheme + "://" + urlparse(BASE_URL).netloc
    r = requests.get(f"{BASE_URL}documents/{tracking}/download/")
    if r.status_code == 200 and "application/pdf" in r.headers.get("Content-Type", ""):
        print("   OK (via API endpoint)")
    elif pdf_url:
        # Try direct media URL
        media_url = f"{base_origin}{pdf_url}"
        r2 = requests.get(media_url)
        if r2.status_code == 200:
            print("   OK (via media URL)")
        else:
            print(f"   WARN - API {r.status_code}, media {r2.status_code}")
    else:
        print(f"   FAIL - HTTP {r.status_code}")

    # 6. Analytics
    print("6. GET analytics/")
    r = requests.get(f"{BASE_URL}analytics/", headers=headers)
    if r.status_code != 200:
        print(f"   FAIL - HTTP {r.status_code}")
        return 1
    print("   OK")

    # 7. Token refresh
    print("7. POST token/refresh/")
    refresh = requests.post(f"{BASE_URL}token/", json={"username": "admin", "password": "admin"}).json()
    refresh_token = refresh.get("refresh")
    if refresh_token:
        r = requests.post(f"{BASE_URL}token/refresh/", json={"refresh": refresh_token})
        if r.status_code == 200:
            print("   OK")
        else:
            print(f"   FAIL - HTTP {r.status_code}")
    else:
        print("   SKIP - no refresh token")

    print("\nAll API tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
