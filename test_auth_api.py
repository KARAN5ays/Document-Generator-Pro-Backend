import requests
import json
import uuid

BASE_URL = "http://localhost:8000/api"

def test_auth_flow():
    test_username = f"testuser_{uuid.uuid4().hex[:6]}"
    test_password = "securepassword123"
    test_email = f"{test_username}@example.com"
    
    print("\n=== Testing Registration ===")
    reg_response = requests.post(f"{BASE_URL}/register/", json={
        "username": test_username,
        "email": test_email,
        "password": test_password
    })
    
    if reg_response.status_code == 201:
        print("✅ Registration successful")
        data = reg_response.json()
        token = data.get('access')
        print(f"Token received upon registration: {'Yes' if token else 'No'}")
    else:
        print(f"❌ Registration failed: {reg_response.status_code} - {reg_response.text}")
        return

    print("\n=== Testing Login ===")
    login_response = requests.post(f"{BASE_URL}/token/", json={
        "username": test_username,
        "password": test_password
    })
    
    if login_response.status_code == 200:
        print("✅ Login successful")
        new_token = login_response.json().get('access')
        print(f"New access token received: {'Yes' if new_token else 'No'}")
        
        # Test document retrieval for this new user
        print("\n=== Testing User Documents (Should be empty) ===")
        docs_response = requests.get(f"{BASE_URL}/documents/", headers={"Authorization": f"Bearer {new_token}"})
        if docs_response.status_code == 200:
            docs = docs_response.json()
            print(f"✅ Document retrieve successful. Count: {len(docs)}")
            if len(docs) == 0:
                print("✅ Correctly isolated to 0 documents for new user.")
            else:
                print("❌ User isolation failed! New user sees existing documents.")
        else:
            print(f"❌ Document fetch failed: {docs_response.status_code} - {docs_response.text}")
    else:
        print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")

if __name__ == "__main__":
    test_auth_flow()
