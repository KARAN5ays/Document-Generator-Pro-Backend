import requests
import uuid

BASE_URL = "http://localhost:8000/api"

def create_user():
    username = f"user_{uuid.uuid4().hex[:6]}"
    password = "securepassword123"
    email = f"{username}@example.com"
    
    reg_response = requests.post(f"{BASE_URL}/register/", json={
        "username": username,
        "email": email,
        "password": password
    })
    return reg_response.json().get('access'), username

def get_templates(token):
    res = requests.get(f"{BASE_URL}/document-types/", headers={"Authorization": f"Bearer {token}"})
    return res.json() if res.status_code == 200 else []

def create_template(token, name):
    res = requests.post(f"{BASE_URL}/document-types/", headers={"Authorization": f"Bearer {token}"}, json={
        "name": name,
        "template_html": f"<h1>{name}</h1>"
    })
    return res.json() if res.status_code == 201 else None

def test_template_isolation():
    print("Testing template isolation...")
    
    # 1. Create User A
    token_a, user_a = create_user()
    print(f"Created {user_a}")
    
    # 2. Assert templates list length (should be the default global ones, let's say N)
    templates_a = get_templates(token_a)
    initial_count = len(templates_a)
    print(f"User A sees {initial_count} templates initially.")
    
    # 3. Create Custom Template for User A
    custom_name = f"Custom_{user_a}"
    create_template(token_a, custom_name)
    print(f"User A created: {custom_name}")
    
    # 4. Assert User A sees N+1 templates
    templates_a_updated = get_templates(token_a)
    print(f"User A sees {len(templates_a_updated)} templates after creating one.")
    assert len(templates_a_updated) == initial_count + 1, "User A should see the new template"
    
    # 5. Create User B
    token_b, user_b = create_user()
    print(f"Created {user_b}")
    
    # 6. Assert User B only sees N templates (isolated from User A)
    templates_b = get_templates(token_b)
    print(f"User B sees {len(templates_b)} templates initially.")
    
    if len(templates_b) == initial_count:
        print("✅ SUCCESS: User B does not see User A's custom template! Isolation is working.")
    else:
        print("❌ FAILED: User B saw incorrect number of templates.")

if __name__ == "__main__":
    test_template_isolation()
