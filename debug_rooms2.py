#!/usr/bin/env python3
import os, django, sys
sys.path.insert(0, 'backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

import requests
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User

user = User.objects.get(email='testreceptionist@hotel.com')
token = str(RefreshToken.for_user(user).access_token)
headers = {'Authorization': f'Bearer {token}'}

# Test without filter
print('Without filter:')
response = requests.get('http://localhost:8000/api/rooms/', headers=headers)
data = response.json()
print(f'  Total count: {data.get("count", 0)}')
print(f'  Results: {len(data.get("results", []))}')

# Test with status filter UPPERCASE
print('With status=AVAILABLE filter (uppercase):')
response = requests.get('http://localhost:8000/api/rooms/?status=AVAILABLE', headers=headers)
data = response.json()
print(f'  Total count: {data.get("count", 0)}')
print(f'  Results: {len(data.get("results", []))}')

# Test with lowercase
print('With status=available filter (lowercase):')
response = requests.get('http://localhost:8000/api/rooms/?status=available', headers=headers)
data = response.json()
print(f'  Total count: {data.get("count", 0)}')
print(f'  Results: {len(data.get("results", []))}')
