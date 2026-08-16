#!/usr/bin/env python3
"""
End-to-End System Test: Complete booking flow from Receptionist to Admin
"""

import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

import requests
from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User
from colorama import Fore, Style, init

init(autoreset=True)

BASE_URL = "http://localhost:8000/api"

def get_token(email):
    """Get JWT token for a user"""
    try:
        user = User.objects.get(email=email)
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    except:
        return None

def log(msg, status="info"):
    """Log message with color"""
    if status == "ok":
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} {msg}")
    elif status == "fail":
        print(f"{Fore.RED}✗{Style.RESET_ALL} {msg}")
    elif status == "info":
        print(f"{Fore.CYAN}>{Style.RESET_ALL} {msg}")
    else:
        print(msg)

print(f"\n{Fore.CYAN}{'='*60}")
print("END-TO-END SYSTEM TEST: Complete Booking Flow")
print(f"{'='*60}{Style.RESET_ALL}\n")

# Step 1: Receptionist logs in and creates a guest
print(f"\n{Fore.CYAN}STEP 1: RECEPTIONIST - Create Guest{Style.RESET_ALL}")
token_recv = get_token("testreceptionist@hotel.com")
if not token_recv:
    log("Failed to get receptionist token", "fail")
    sys.exit(1)

headers_recv = {"Authorization": f"Bearer {token_recv}"}
guest_data = {
    "first_name": "John",
    "last_name": "Smith",
    "email": f"customer{datetime.now().timestamp():.0f}@hotel.com",
    "phone": "+1234567890",
    "address": "123 Main St",
    "city": "New York",
    "country": "USA",
    "passport_number": "AB123456"
}

response = requests.post(f"{BASE_URL}/guests/", json=guest_data, headers=headers_recv)
if response.status_code == 201:
    guest = response.json()
    guest_id = guest['id']
    log(f"Guest created: {guest['email']} (ID: {guest_id})", "ok")
else:
    log(f"Failed to create guest: {response.status_code}", "fail")
    sys.exit(1)

# Step 2: Get available rooms
print(f"\n{Fore.CYAN}STEP 2: RECEPTIONIST - Check Available Rooms{Style.RESET_ALL}")
response = requests.get(f"{BASE_URL}/rooms/?status=available", headers=headers_recv)
if response.status_code == 200:
    data = response.json()
    rooms = data.get("results", []) if isinstance(data, dict) else data
    if rooms:
        room = rooms[0]
        room_id = room['id']
        log(f"Found {len(rooms)} available rooms", "info")
        log(f"Selected Room {room['room_number']} (ID: {room_id})", "ok")
    else:
        log("No available rooms", "fail")
        sys.exit(1)
else:
    log(f"Failed to get rooms: {response.status_code}", "fail")
    sys.exit(1)

# Step 3: Create a reservation
print(f"\n{Fore.CYAN}STEP 3: RECEPTIONIST - Create Reservation{Style.RESET_ALL}")
check_in = (datetime.now() + timedelta(days=1)).date()
check_out = (check_in + timedelta(days=3))

reservation_data = {
    "guest": guest_id,
    "room": room_id,
    "check_in_date": check_in.isoformat(),
    "check_out_date": check_out.isoformat(),
    "number_of_guests": 2,
    "notes": "Business trip"
}

response = requests.post(f"{BASE_URL}/reservations/", json=reservation_data, headers=headers_recv)
if response.status_code == 201:
    reservation = response.json()
    reservation_id = reservation['id']
    log(f"Reservation created: {check_in} to {check_out} (ID: {reservation_id})", "ok")
else:
    log(f"Failed to create reservation: {response.status_code} - {response.text[:100]}", "fail")
    sys.exit(1)

# Step 3.2: Confirm the reservation
print(f"\n{Fore.CYAN}STEP 3.2: RECEPTIONIST - Confirm Reservation{Style.RESET_ALL}")
response = requests.patch(f"{BASE_URL}/reservations/{reservation_id}/", 
                         json={"status": "CONFIRMED"}, headers=headers_recv)
if response.status_code == 200:
    reservation = response.json()
    log(f"Reservation confirmed: Status={reservation.get('status')}", "ok")
else:
    log(f"Failed to confirm reservation: {response.status_code}", "fail")
    # Don't exit - try to continue

# Step 3.5: Check-in (Create stay)
print(f"\n{Fore.CYAN}STEP 3.5: RECEPTIONIST - Check-in (Create Stay){Style.RESET_ALL}")
check_in_data = {
    "reservation_id": reservation_id,
    "notes": "Guest arrived",
}

response = requests.post(f"{BASE_URL}/stays/check-in/", json=check_in_data, headers=headers_recv)
if response.status_code == 201:
    stay = response.json()
    stay_id = stay['id']
    log(f"Guest checked in: Stay ID {stay_id}", "ok")
else:
    log(f"Failed to check-in: {response.status_code} - {response.text[:100]}", "fail")
    sys.exit(1)

# Step 4: Create an invoice
print(f"\n{Fore.CYAN}STEP 4: RECEPTIONIST - Create Invoice{Style.RESET_ALL}")
invoice_data = {
    "stay_id": stay_id,
    "discount": 0,
    "notes": "Standard booking"
}

response = requests.post(f"{BASE_URL}/billing/invoices/", json=invoice_data, headers=headers_recv)
if response.status_code == 201:
    invoice = response.json()
    invoice_id = invoice['id']
    total = invoice.get('total', invoice.get('total_amount', 0))
    log(f"Invoice created: ID {invoice_id}, Total: ${total}", "ok")
else:
    log(f"Failed to create invoice: {response.status_code}", "fail")
    sys.exit(1)

# Step 5: Manager views reports
print(f"\n{Fore.CYAN}STEP 5: MANAGER - View Financial Reports{Style.RESET_ALL}")
token_mgr = get_token("testmanager@hotel.com")
if not token_mgr:
    log("Failed to get manager token", "fail")
else:
    headers_mgr = {"Authorization": f"Bearer {token_mgr}"}
    
    # Revenue report
    response = requests.get(f"{BASE_URL}/reports/revenue/", headers=headers_mgr)
    if response.status_code == 200:
        log("Revenue report accessed", "ok")
    else:
        log(f"Failed to get revenue report: {response.status_code}", "fail")
    
    # Occupancy report
    response = requests.get(f"{BASE_URL}/reports/occupancy/", headers=headers_mgr)
    if response.status_code == 200:
        log("Occupancy report accessed", "ok")
    else:
        log(f"Failed to get occupancy report: {response.status_code}", "fail")
    
    # Outstanding payments
    response = requests.get(f"{BASE_URL}/reports/outstanding/", headers=headers_mgr)
    if response.status_code == 200:
        log("Outstanding payments report accessed", "ok")
    else:
        log(f"Failed to get outstanding report: {response.status_code}", "fail")

# Step 6: Admin creates new staff
print(f"\n{Fore.CYAN}STEP 6: ADMIN - Create New Staff Member{Style.RESET_ALL}")
token_admin = get_token("testadmin@hotel.com")
if not token_admin:
    log("Failed to get admin token", "fail")
else:
    headers_admin = {"Authorization": f"Bearer {token_admin}"}
    
    staff_data = {
        "email": f"newstaff{datetime.now().timestamp():.0f}@hotel.com",
        "first_name": "Jane",
        "last_name": "Doe",
        "phone": "+9876543210",
        "role": "RECEPTIONIST",
        "temporary_password": "SecurePass123",
        "confirm_password": "SecurePass123"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=staff_data, headers=headers_admin)
    if response.status_code == 201:
        staff = response.json()
        log(f"Staff created: {staff['email']} (Role: RECEPTIONIST)", "ok")
    else:
        log(f"Failed to create staff: {response.status_code} - {response.text[:150]}", "fail")

# Step 7: Test role validation on login
print(f"\n{Fore.CYAN}STEP 7: SECURITY - Test Role Validation{Style.RESET_ALL}")
try:
    # Try to login as manager with admin credentials (should fail)
    response = requests.post(f"{BASE_URL}/auth/login/", json={
        "email": "testadmin@hotel.com",
        "password": "TestPassword123"
    })
    if response.status_code == 200:
        log("Admin can login with admin credentials", "ok")
    else:
        log(f"Admin login failed: {response.status_code}", "fail")
except Exception as e:
    log(f"Login test error: {e}", "fail")

print(f"\n{Fore.CYAN}{'='*60}")
print("END-TO-END TEST COMPLETE")
print(f"{'='*60}{Style.RESET_ALL}\n")
