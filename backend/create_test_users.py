#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.accounts.models import User, Role

# Create or get roles
receptionist_role = Role.objects.get_or_create(name='RECEPTIONIST')[0]
manager_role = Role.objects.get_or_create(name='MANAGER')[0]
admin_role = Role.objects.get_or_create(name='ADMIN')[0]

# Create test users if they don't exist
users_to_create = [
    {'email': 'testreceptionist@hotel.com', 'password': 'TestPassword123', 'role': receptionist_role, 'first_name': 'Test', 'last_name': 'Receptionist'},
    {'email': 'testmanager@hotel.com', 'password': 'TestPassword123', 'role': manager_role, 'first_name': 'Test', 'last_name': 'Manager'},
]

for user_data in users_to_create:
    email = user_data.pop('email')
    password = user_data.pop('password')
    role = user_data['role']
    
    user, created = User.objects.get_or_create(email=email, defaults=user_data)
    if created:
        user.set_password(password)
        user.save()
        print(f'Created: {email} ({role.name})')
    else:
        print(f'Exists: {email} ({user.role})')

print('\nAll users:')
for user in User.objects.all():
    print(f'  - {user.email}: {user.role}')
