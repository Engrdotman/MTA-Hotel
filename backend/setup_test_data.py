#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.rooms.models import Room, RoomType
from apps.accounts.models import User, Role

print("=" * 50)
print("SETTING UP TEST DATA")
print("=" * 50)

# 1. Create room types
print("\n1. Creating Room Types...")
room_types = [
    {'name': 'Standard', 'description': 'Standard room with basic amenities', 'capacity': 2, 'base_price': 100},
    {'name': 'Deluxe', 'description': 'Deluxe room with premium amenities', 'capacity': 3, 'base_price': 150},
    {'name': 'Suite', 'description': 'Luxury suite with full amenities', 'capacity': 4, 'base_price': 250},
]

for rt_data in room_types:
    rt, created = RoomType.objects.get_or_create(name=rt_data['name'], defaults={
        'description': rt_data['description'],
        'capacity': rt_data['capacity'],
        'base_price': rt_data['base_price']
    })
    if created:
        print(f"  ✓ Created: {rt.name} (${rt.base_price}/night)")
    else:
        print(f"  - Exists: {rt.name}")

# 2. Create rooms
print("\n2. Creating Rooms...")
standard_type = RoomType.objects.get(name='Standard')
deluxe_type = RoomType.objects.get(name='Deluxe')

rooms_to_create = [
    {'room_number': '101', 'room_type': standard_type},
    {'room_number': '102', 'room_type': standard_type},
    {'room_number': '201', 'room_type': deluxe_type},
    {'room_number': '202', 'room_type': deluxe_type},
    {'room_number': '301', 'room_type': deluxe_type},
    {'room_number': '302', 'room_type': standard_type},
]

for room_data in rooms_to_create:
    room, created = Room.objects.get_or_create(room_number=room_data['room_number'], defaults=room_data)
    if created:
        print(f"  ✓ Created: Room {room.room_number} ({room.room_type.name})")
    else:
        print(f"  - Exists: Room {room.room_number}")

# 3. Verify Admin user
print("\n3. Verifying Admin User...")
admin_role = Role.objects.get_or_create(name='ADMIN')[0]
admin_user, created = User.objects.get_or_create(
    email='testadmin@hotel.com',
    defaults={
        'first_name': 'Test',
        'last_name': 'Admin',
        'role': admin_role,
        'is_active': True,
        'is_staff': True,
    }
)
if created:
    admin_user.set_password('TestPassword123')
    admin_user.save()
    print(f"  ✓ Created: Admin user (testadmin@hotel.com)")
else:
    # Update password to ensure it's correct
    admin_user.set_password('TestPassword123')
    admin_user.save()
    print(f"  ✓ Updated: Admin user (testadmin@hotel.com)")

print("\n" + "=" * 50)
print("SETUP COMPLETE")
print("=" * 50)
