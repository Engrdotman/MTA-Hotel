#!/usr/bin/env python3
import os
import sys
import django

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

import requests
import json
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User

BASE_URL = "http://localhost:8000/api"

# Get token
user = User.objects.get(email="testreceptionist@hotel.com")
refresh = RefreshToken.for_user(user)
token = str(refresh.access_token)

headers = {"Authorization": f"Bearer {token}"}

# Test endpoints
endpoints = [
    ("/rooms/?status=available", "Rooms"),
    ("/users/", "Users List"),
    ("/audit-logs/", "Audit Log"),
    ("/reports/system-statistics/", "System Stats"),
]

for endpoint, name in endpoints:
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
        print(f"\n{name}:")
        print(f"  Status: {response.status_code}")
        try:
            data = response.json()
            print(f"  Response type: {type(data).__name__}")
            if isinstance(data, dict):
                print(f"  Keys: {list(data.keys())[:5]}")
                if "results" in data:
                    print(f"  Results count: {len(data['results'])}")
            elif isinstance(data, list):
                print(f"  List length: {len(data)}")
        except:
            print(f"  Body: {response.text[:100]}")
    except Exception as e:
        print(f"\n{name}: ERROR - {e}")
