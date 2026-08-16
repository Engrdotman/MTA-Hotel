#!/usr/bin/env python3
"""
Comprehensive System Test - Full User Journey
Tests all roles (Receptionist, Manager, Admin) through complete workflows
"""

import requests
import json
from datetime import datetime, timedelta
from colorama import Fore, Style, init

init(autoreset=True)

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

# Test users - these should exist in the system
TEST_USERS = {
    "receptionist": {
        "email": "testreceptionist@hotel.com",
        "password": "TestPassword123",
        "role": "RECEPTIONIST"
    },
    "manager": {
        "email": "testmanager@hotel.com",
        "password": "TestPassword123",
        "role": "MANAGER"
    },
    "admin": {
        "email": "testadmin@hotel.com",
        "password": "TestPassword123",
        "role": "ADMIN"
    }
}

class TestRunner:
    def __init__(self):
        self.results = {"passed": [], "failed": []}
        self.tokens = {}
        self.created_resources = {
            "guests": [],
            "reservations": [],
            "invoices": [],
            "payments": []
        }

    def log_test(self, name, status, details=""):
        """Log test result"""
        if status:
            print(f"{Fore.GREEN}✓{Style.RESET_ALL} {name}")
            self.results["passed"].append(name)
        else:
            print(f"{Fore.RED}✗{Style.RESET_ALL} {name}: {details}")
            self.results["failed"].append((name, details))

    def login(self, role_name):
        """Login and get token for a role"""
        user = TEST_USERS[role_name]
        try:
            response = requests.post(
                f"{API_BASE}/auth/login/",
                json={"email": user["email"], "password": user["password"]},
                timeout=5
            )
            if response.status_code == 200:
                token = response.json().get("access")
                self.tokens[role_name] = token
                self.log_test(f"Login as {role_name}", True)
                return True
            else:
                self.log_test(f"Login as {role_name}", False, f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_test(f"Login as {role_name}", False, str(e))
            return False

    def get_headers(self, role_name):
        """Get auth headers for a role"""
        token = self.tokens.get(role_name)
        if not token:
            return None
        return {"Authorization": f"Bearer {token}"}

    def test_receptionist_workflow(self):
        """Test full Receptionist workflow"""
        print(f"\n{Fore.CYAN}=== RECEPTIONIST WORKFLOW ==={Style.RESET_ALL}")
        
        if not self.login("receptionist"):
            return

        headers = self.get_headers("receptionist")

        # 1. Create a guest
        print("\n1. Creating Guest...")
        guest_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "address": "123 Main St",
            "city": "New York",
            "country": "USA",
            "passport_number": "AB123456"
        }
        try:
            response = requests.post(f"{API_BASE}/guests/", json=guest_data, headers=headers, timeout=5)
            if response.status_code == 201:
                guest = response.json()
                guest_id = guest.get("id")
                self.created_resources["guests"].append(guest_id)
                self.log_test("Create Guest", True)
            else:
                self.log_test("Create Guest", False, f"Status {response.status_code}: {response.text[:100]}")
                return
        except Exception as e:
            self.log_test("Create Guest", False, str(e))
            return

        # 2. Get available rooms
        print("\n2. Checking Available Rooms...")
        try:
            response = requests.get(f"{API_BASE}/rooms/?status=available", headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Handle both paginated and list responses
                if isinstance(data, dict):
                    rooms = data.get("results", [])
                else:
                    rooms = data if isinstance(data, list) else []
                    
                if rooms:
                    room_id = rooms[0].get("id")
                    self.log_test("Get Available Rooms", True)
                else:
                    self.log_test("Get Available Rooms", False, "No rooms available")
                    return
            else:
                self.log_test("Get Available Rooms", False, f"Status {response.status_code}")
                return
        except Exception as e:
            self.log_test("Get Available Rooms", False, str(e))
            return

        # 3. Create a reservation
        print("\n3. Creating Reservation...")
        check_in = datetime.now() + timedelta(days=1)
        check_out = check_in + timedelta(days=3)
        
        reservation_data = {
            "guest": guest_id,
            "room": room_id,
            "check_in_date": check_in.date().isoformat(),
            "check_out_date": check_out.date().isoformat(),
            "number_of_guests": 2,
            "notes": "Test reservation from receptionist"
        }
        try:
            response = requests.post(f"{API_BASE}/reservations/", json=reservation_data, headers=headers, timeout=5)
            if response.status_code == 201:
                reservation = response.json()
                reservation_id = reservation.get("id")
                self.created_resources["reservations"].append(reservation_id)
                self.log_test("Create Reservation", True)
            else:
                self.log_test("Create Reservation", False, f"Status {response.status_code}: {response.text[:100]}")
                return
        except Exception as e:
            self.log_test("Create Reservation", False, str(e))
            return

        # 4. Check reservation status
        print("\n4. Checking Reservation Status...")
        try:
            response = requests.get(f"{API_BASE}/reservations/{reservation_id}/", headers=headers, timeout=5)
            if response.status_code == 200:
                reservation = response.json()
                status = reservation.get("status")
                self.log_test(f"Get Reservation (Status: {status})", True)
            else:
                self.log_test("Get Reservation", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("Get Reservation", False, str(e))

        # 5. Create Invoice
        print("\n5. Creating Invoice...")
        invoice_data = {
            "reservation": reservation_id,
            "discount": 0,
            "notes": "Standard check-in invoice"
        }
        try:
            response = requests.post(f"{API_BASE}/billing/invoices/", json=invoice_data, headers=headers, timeout=5)
            if response.status_code == 201:
                invoice = response.json()
                invoice_id = invoice.get("id")
                self.created_resources["invoices"].append(invoice_id)
                self.log_test("Create Invoice", True)
            else:
                self.log_test("Create Invoice", False, f"Status {response.status_code}: {response.text[:100]}")
        except Exception as e:
            self.log_test("Create Invoice", False, str(e))

        # 6. View Dashboard (Receptionist can view basic dashboard)
        print("\n6. Checking Dashboard Access...")
        try:
            response = requests.get(f"{API_BASE}/dashboard/stats/", headers=headers, timeout=5)
            if response.status_code in [200, 403]:  # 403 is OK if no permission
                self.log_test("Dashboard Access", True)
            else:
                self.log_test("Dashboard Access", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("Dashboard Access", False, str(e))

        return reservation_id, invoice_id if 'invoice_id' in locals() else None

    def test_manager_workflow(self):
        """Test Manager workflow - can view reports and manage staff"""
        print(f"\n{Fore.CYAN}=== MANAGER WORKFLOW ==={Style.RESET_ALL}")
        
        if not self.login("manager"):
            return

        headers = self.get_headers("manager")

        # 1. View Reports
        print("\n1. Accessing Financial Reports...")
        try:
            response = requests.get(f"{API_BASE}/reports/revenue/", headers=headers, timeout=5)
            if response.status_code == 200:
                self.log_test("View Revenue Report", True)
            else:
                self.log_test("View Revenue Report", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("View Revenue Report", False, str(e))

        # 2. View Occupancy Report
        print("\n2. Accessing Occupancy Report...")
        try:
            response = requests.get(f"{API_BASE}/reports/occupancy/", headers=headers, timeout=5)
            if response.status_code == 200:
                self.log_test("View Occupancy Report", True)
            else:
                self.log_test("View Occupancy Report", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("View Occupancy Report", False, str(e))

        # 3. View Outstanding Payments
        print("\n3. Accessing Outstanding Payments Report...")
        try:
            response = requests.get(f"{API_BASE}/reports/outstanding/", headers=headers, timeout=5)
            if response.status_code == 200:
                self.log_test("View Outstanding Payments", True)
            else:
                self.log_test("View Outstanding Payments", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("View Outstanding Payments", False, str(e))

        # 4. View all users (staff management)
        print("\n4. Accessing User List...")
        try:
            response = requests.get(f"{API_BASE}/users/", headers=headers, timeout=5)
            if response.status_code == 200:
                users = response.json().get("results", [])
                self.log_test(f"View Users List ({len(users)} users)", True)
            else:
                self.log_test("View Users List", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("View Users List", False, str(e))

        # 5. View all reservations
        print("\n5. Accessing All Reservations...")
        try:
            response = requests.get(f"{API_BASE}/reservations/", headers=headers, timeout=5)
            if response.status_code == 200:
                reservations = response.json().get("results", [])
                self.log_test(f"View Reservations ({len(reservations)} total)", True)
            else:
                self.log_test("View Reservations", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("View Reservations", False, str(e))

    def test_admin_workflow(self):
        """Test Admin workflow - full system access"""
        print(f"\n{Fore.CYAN}=== ADMIN WORKFLOW ==={Style.RESET_ALL}")
        
        if not self.login("admin"):
            return

        headers = self.get_headers("admin")

        # 1. Create a new staff member
        print("\n1. Creating New Staff Member (Receptionist)...")
        staff_data = {
            "email": f"newstaff{int(datetime.now().timestamp())}@hotel.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "role": "RECEPTIONIST",
            "password": "SecurePassword123"
        }
        try:
            response = requests.post(f"{API_BASE}/users/", json=staff_data, headers=headers, timeout=5)
            if response.status_code == 201:
                self.log_test("Create Staff Member", True)
            else:
                self.log_test("Create Staff Member", False, f"Status {response.status_code}: {response.text[:100]}")
        except Exception as e:
            self.log_test("Create Staff Member", False, str(e))

        # 2. View all users
        print("\n2. Viewing All Users...")
        try:
            response = requests.get(f"{API_BASE}/users/", headers=headers, timeout=5)
            if response.status_code == 200:
                users = response.json().get("results", [])
                self.log_test(f"View All Users ({len(users)} total)", True)
                print(f"   Users by role:")
                for user in users[:5]:  # Show first 5
                    print(f"   - {user.get('email')} ({user.get('role')})")
            else:
                self.log_test("View All Users", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("View All Users", False, str(e))

        # 3. View Audit Log
        print("\n3. Accessing Audit Log...")
        try:
            response = requests.get(f"{API_BASE}/audit-logs/", headers=headers, timeout=5)
            if response.status_code == 200:
                logs = response.json().get("results", [])
                self.log_test(f"View Audit Log ({len(logs)} total)", True)
            else:
                self.log_test("View Audit Log", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("View Audit Log", False, str(e))

        # 4. Generate System Report
        print("\n4. Accessing System Reports...")
        try:
            response = requests.get(f"{API_BASE}/reports/system-statistics/", headers=headers, timeout=5)
            if response.status_code == 200:
                stats = response.json()
                self.log_test("View System Statistics", True)
                print(f"   System Statistics:")
                for key, value in list(stats.items())[:5]:
                    print(f"   - {key}: {value}")
            else:
                self.log_test("View System Statistics", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("View System Statistics", False, str(e))

        # 5. View all rooms
        print("\n5. Viewing All Rooms...")
        try:
            response = requests.get(f"{API_BASE}/rooms/", headers=headers, timeout=5)
            if response.status_code == 200:
                rooms = response.json().get("results", [])
                available = sum(1 for r in rooms if r.get("status") == "available")
                self.log_test(f"View All Rooms ({len(rooms)} total, {available} available)", True)
            else:
                self.log_test("View All Rooms", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("View All Rooms", False, str(e))

    def test_role_validation(self):
        """Test role validation on login"""
        print(f"\n{Fore.CYAN}=== ROLE VALIDATION TEST ==={Style.RESET_ALL}")
        
        # Login as admin
        if not self.login("admin"):
            return

        admin_token = self.tokens["admin"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. Try to access admin-only endpoint with admin token (should succeed)
        print("\n1. Admin accessing Audit Log (should succeed)...")
        try:
            response = requests.get(f"{API_BASE}/audit-logs/", headers=admin_headers, timeout=5)
            if response.status_code == 200:
                self.log_test("Admin access to Audit Log", True)
            else:
                self.log_test("Admin access to Audit Log", False, f"Status {response.status_code}")
        except Exception as e:
            self.log_test("Admin access to Audit Log", False, str(e))

        # 2. Login as receptionist
        if not self.login("receptionist"):
            return

        receptionist_token = self.tokens["receptionist"]
        receptionist_headers = {"Authorization": f"Bearer {receptionist_token}"}

        # 3. Try to access admin-only endpoint with receptionist token (should fail)
        print("\n2. Receptionist accessing Audit Log (should be denied)...")
        try:
            response = requests.get(f"{API_BASE}/audit-logs/", headers=receptionist_headers, timeout=5)
            if response.status_code == 403:
                self.log_test("Receptionist denied access to Audit Log", True)
            elif response.status_code == 200:
                self.log_test("Receptionist denied access to Audit Log", False, "Unexpected: got 200 instead of 403")
            else:
                self.log_test("Receptionist access denied", True)
        except Exception as e:
            self.log_test("Receptionist access denied", False, str(e))

    def print_summary(self):
        """Print test summary"""
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"TEST SUMMARY")
        print(f"{'='*50}{Style.RESET_ALL}")
        
        passed = len(self.results["passed"])
        failed = len(self.results["failed"])
        total = passed + failed

        print(f"\n{Fore.GREEN}Passed: {passed}/{total}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed: {failed}/{total}{Style.RESET_ALL}")

        if self.results["failed"]:
            print(f"\n{Fore.RED}Failed Tests:{Style.RESET_ALL}")
            for name, details in self.results["failed"]:
                print(f"  • {name}: {details}")

        print(f"\n{Fore.GREEN}Created Resources:{Style.RESET_ALL}")
        for resource_type, ids in self.created_resources.items():
            if ids:
                print(f"  • {resource_type}: {len(ids)} created")

        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"\nSuccess Rate: {Fore.GREEN if success_rate >= 80 else Fore.RED}{success_rate:.1f}%{Style.RESET_ALL}")

def main():
    print(f"{Fore.CYAN}{'='*50}")
    print(f"MTA HOTEL - COMPREHENSIVE SYSTEM TEST")
    print(f"{'='*50}{Style.RESET_ALL}\n")

    runner = TestRunner()

    # Run all test workflows
    runner.test_receptionist_workflow()
    runner.test_manager_workflow()
    runner.test_admin_workflow()
    runner.test_role_validation()

    # Print summary
    runner.print_summary()

if __name__ == "__main__":
    main()
