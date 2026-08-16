#!/usr/bin/env python3
import os, django, sys
sys.path.insert(0, 'backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

import requests
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User
from apps.rooms.models import Room

# Check database first
print("Database check:")
all_rooms = Room.objects.all()
print(f"Total rooms: {all_rooms.count()}")
available_rooms = Room.objects.filter(status='AVAILABLE')
print(f"Available rooms: {available_rooms.count()}")
for room in available_rooms[:3]:
    print(f"  - {room.room_number}: {room.status}")

# Now test API
print("\nAPI check:")
user = User.objects.get(email='testreceptionist@hotel.com')
token = str(RefreshToken.for_user(user).access_token)
headers = {'Authorization': f'Bearer {token}'}

response = requests.get('http://localhost:8000/api/rooms/?status=available', headers=headers)
print(f'Status: {response.status_code}')
data = response.json()
print(f'Response type: {type(data).__name__}')
print(f'Keys: {list(data.keys()) if isinstance(data, dict) else "N/A"}')
if isinstance(data, dict):
    print(f'Results: {len(data.get("results", []))} rooms')
    if data.get('results'):
        print(f'First room: {data["results"][0]}')
