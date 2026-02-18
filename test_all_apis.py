#!/usr/bin/env python3
"""
Comprehensive API test script to verify all endpoints.
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_authentication():
    """Test login endpoint"""
    print("\n=== Testing Authentication ===")
    response = requests.post(f"{BASE_URL}/token/", json={
        "username": "luffy",
        "password": "karan2123"
    })
    print(f"Login: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Access token received")
        return data.get('access')
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_document_types(token):
    """Test document types endpoint"""
    print("\n=== Testing Document Types ===")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # GET document types
    response = requests.get(f"{BASE_URL}/document-types/", headers=headers)
    print(f"GET /document-types/: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Found {len(response.json())} document types")
    else:
        print(f"❌ Failed: {response.text}")

def test_documents(token):
    """Test document endpoints"""
    print("\n=== Testing Documents ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    # GET documents list
    response = requests.get(f"{BASE_URL}/documents/", headers=headers)
    print(f"GET /documents/: {response.status_code}")
    if response.status_code == 200:
        docs = response.json()
        print(f"✅ Found {len(docs)} documents")
        return docs
    else:
        print(f"❌ Failed: {response.text}")
        return []

def test_analytics(token):
    """Test analytics endpoints"""
    print("\n=== Testing Analytics ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Dashboard analytics
    response = requests.get(f"{BASE_URL}/analytics/", headers=headers)
    print(f"GET /analytics/: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Analytics data received")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Verification stats
    response = requests.get(f"{BASE_URL}/verification-stats/", headers=headers)
    print(f"GET /verification-stats/: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Verification stats received")
    else:
        print(f"❌ Failed: {response.text}")

def test_template_builder(token):
    """Test template builder config"""
    print("\n=== Testing Template Builder ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/template-builder-config/", headers=headers)
    print(f"GET /template-builder-config/: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Template builder config received")
    else:
        print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    print("🔍 Starting comprehensive API test...")
    
    # Test authentication
    token = test_authentication()
    
    if token:
        # Test all endpoints
        test_document_types(token)
        test_documents(token)
        test_analytics(token)
        test_template_builder(token)
        print("\n✅ All API tests completed!")
    else:
        print("\n❌ Cannot proceed without authentication")
