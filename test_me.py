import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DocumentGenerator.settings')
django.setup()

from documentapp.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import requests

u = User.objects.get(username='robin')
print("DB check: id=", u.id, " merchant=", getattr(u, 'merchant_id', None))

refresh = RefreshToken.for_user(u)
token = str(refresh.access_token)

headers = {'Authorization': f'Bearer {token}'}
res = requests.get('http://127.0.0.1:8000/api/users/me/', headers=headers)
print("API Response:", res.status_code, res.json())
