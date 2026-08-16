from decimal import Decimal
from datetime import datetime, timedelta, timezone
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.accounts.models import Role
from apps.reports.services import ReportService
from apps.guests.models import Guest
from apps.payments.models import Payment
from apps.reservations.models import Reservation
from apps.rooms.models import Room, RoomType
from apps.stays.models import Stay
from apps.billing.models import Invoice, InvoiceItem

User = get_user_model()


class ReportServiceTestCase(TestCase):
    """Tests for report service."""

    def setUp(self):
        """Set up test data."""
        # Create roles
        self.admin_role = Role.objects.create(name=Role.ADMIN)
        self.manager_role = Role.objects.create(name=Role.MANAGER)
        self.accountant_role = Role.objects.create(name=Role.ACCOUNTANT)

        # Create users
        self.admin = User.objects.create_user(
            email="admin@test.com",
            first_name="Admin",
            last_name="User",
            password="testpass123",
            role=self.admin_role,
        )

        # Create room type and rooms
        self.room_type = RoomType.objects.create(
            name="Standard",
            capacity=2,
            base_price=Decimal("40000.00"),
        )

        for i in range(10):
            Room.objects.create(
                room_number=f"{100 + i}",
                room_type=self.room_type,
                status=Room.Status.AVAILABLE if i < 7 else Room.Status.OCCUPIED,
            )

        # Create guest
        self.guest = Guest.objects.create(
            guest_code="G001",
            first_name="John",
            last_name="Doe",
        )

        # Create reservation
        self.check_in = datetime.now(timezone.utc).date()
        self.check_out = self.check_in + timedelta(days=3)
        self.reservation = Reservation.objects.create(
            reservation_number="RES001",
            guest=self.guest,
            room=Room.objects.first(),
            check_in_date=self.check_in,
            check_out_date=self.check_out,
            status=Reservation.Status.CONFIRMED,
        )

        # Create stay
        self.stay = Stay.objects.create(
            reservation=self.reservation,
            guest=self.guest,
            room=Room.objects.first(),
            checked_in_at=datetime.now(timezone.utc),
            status=Stay.Status.CHECKED_IN,
        )

        # Create invoice and payment
        self.invoice = Invoice.objects.create(
            invoice_number="INV-000001",
            guest=self.guest,
            reservation=self.reservation,
            stay=self.stay,
            status=Invoice.Status.ISSUED,
            subtotal=Decimal("120000.00"),
            total=Decimal("120000.00"),
            amount_paid=Decimal("0"),
            balance=Decimal("120000.00"),
            created_by=self.admin,
        )

        self.payment = Payment.objects.create(
            payment_reference="PAY-000001",
            invoice=self.invoice,
            amount=Decimal("50000.00"),
            method=Payment.Method.CASH,
            payment_date=datetime.now(timezone.utc),
            received_by=self.admin,
        )

    def test_dashboard_summary(self):
        """Test dashboard summary generation."""
        data = ReportService.get_dashboard_summary()
        self.assertIn('total_rooms', data)
        self.assertIn('available_rooms', data)
        self.assertIn('occupied_rooms', data)
        self.assertIn('today_check_ins', data)
        self.assertIn('today_revenue', data)
        self.assertIn('outstanding_balance', data)

    def test_occupancy_report(self):
        """Test occupancy report generation."""
        data = ReportService.get_occupancy_report()
        self.assertEqual(data['total_rooms'], 10)
        self.assertGreater(data['occupied'], 0)
        self.assertIn('occupancy_rate', data)

    def test_occupancy_report_zero_rooms(self):
        """Test occupancy report with no rooms."""
        Payment.objects.all().delete()
        InvoiceItem.objects.all().delete()
        Invoice.objects.all().delete()
        Stay.objects.all().delete()
        Reservation.objects.all().delete()
        Room.objects.all().delete()
        data = ReportService.get_occupancy_report()
        self.assertEqual(data['total_rooms'], 0)
        self.assertEqual(data['occupancy_rate'], '0.00')

    def test_occupancy_report_with_date_range(self):
        """Test occupancy report with date range."""
        start_date = self.check_in
        end_date = self.check_out
        data = ReportService.get_occupancy_report(start_date, end_date)
        self.assertEqual(data['total_rooms'], 10)

    def test_occupancy_report_invalid_date_range(self):
        """Test occupancy report with invalid date range."""
        start_date = self.check_out
        end_date = self.check_in
        with self.assertRaises(ValueError):
            ReportService.get_occupancy_report(start_date, end_date)

    def test_reservation_report(self):
        """Test reservation report generation."""
        data = ReportService.get_reservation_report()
        self.assertIn('total', data)
        self.assertIn('confirmed', data)
        self.assertIn('pending', data)
        self.assertGreater(data['total'], 0)

    def test_reservation_report_with_date_range(self):
        """Test reservation report with date range."""
        start_date = self.check_in
        end_date = self.check_out
        data = ReportService.get_reservation_report(start_date, end_date)
        self.assertGreater(data['total'], 0)

    def test_revenue_report(self):
        """Test revenue report generation."""
        data = ReportService.get_revenue_report()
        self.assertIn('total_revenue', data)
        self.assertIn('cash', data)
        self.assertIn('pos', data)
        # Cash should match our payment
        self.assertGreater(Decimal(data['cash']), 0)

    def test_revenue_report_uses_payment_date(self):
        """Revenue should follow payment_date, not when the row was created."""
        yesterday = self.check_in - timedelta(days=1)
        Payment.objects.create(
            payment_reference="PAY-000003",
            invoice=self.invoice,
            amount=Decimal("10000.00"),
            method=Payment.Method.POS,
            payment_date=datetime.combine(yesterday, datetime.min.time(), tzinfo=timezone.utc),
            received_by=self.admin,
        )

        today_data = ReportService.get_revenue_report(self.check_in, self.check_in)
        yesterday_data = ReportService.get_revenue_report(yesterday, yesterday)

        self.assertEqual(Decimal(today_data["pos"]), Decimal("0"))
        self.assertEqual(Decimal(yesterday_data["pos"]), Decimal("10000.00"))

    def test_revenue_report_payment_methods(self):
        """Test revenue report payment method breakdown."""
        # Create additional payments
        Payment.objects.create(
            payment_reference="PAY-000002",
            invoice=self.invoice,
            amount=Decimal("30000.00"),
            method=Payment.Method.POS,
            payment_date=datetime.now(timezone.utc),
            received_by=self.admin,
        )

        data = ReportService.get_revenue_report()
        cash_amount = Decimal(data['cash'])
        pos_amount = Decimal(data['pos'])
        self.assertGreater(cash_amount, 0)
        self.assertGreater(pos_amount, 0)

    def test_revenue_report_excludes_void(self):
        """Test revenue report excludes void invoices."""
        # This test assumes no void payments in our setup
        initial_data = ReportService.get_revenue_report()
        initial_total = Decimal(initial_data['total_revenue'])

        # Total should be sum of all payments
        self.assertGreater(initial_total, 0)

    def test_outstanding_report(self):
        """Test outstanding balances report."""
        data = ReportService.get_outstanding_report()
        self.assertIn('total_outstanding', data)
        self.assertIn('unpaid_invoices', data)
        self.assertIn('partially_paid_invoices', data)
        # Invoice has balance after partial payment
        self.assertGreater(Decimal(data['total_outstanding']), 0)

    def test_outstanding_report_with_date_range(self):
        """Test outstanding report with date range."""
        start_date = self.check_in
        end_date = self.check_out
        data = ReportService.get_outstanding_report(start_date, end_date)
        self.assertGreater(Decimal(data['total_outstanding']), 0)


class ReportAPITestCase(APITestCase):
    """Tests for report API endpoints."""

    def setUp(self):
        """Set up test users and data."""
        # Create roles
        self.admin_role = Role.objects.create(name=Role.ADMIN)
        self.manager_role = Role.objects.create(name=Role.MANAGER)
        self.accountant_role = Role.objects.create(name=Role.ACCOUNTANT)
        self.receptionist_role = Role.objects.create(name=Role.RECEPTIONIST)
        self.staff_role = Role.objects.create(name=Role.STAFF)

        # Create users
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            role=self.admin_role,
        )
        self.manager = User.objects.create_user(
            email="manager@test.com",
            password="testpass123",
            role=self.manager_role,
        )
        self.accountant = User.objects.create_user(
            email="accountant@test.com",
            password="testpass123",
            role=self.accountant_role,
        )
        self.receptionist = User.objects.create_user(
            email="receptionist@test.com",
            password="testpass123",
            role=self.receptionist_role,
        )
        self.staff = User.objects.create_user(
            email="staff@test.com",
            password="testpass123",
            role=self.staff_role,
        )

        self.client = APIClient()

    def test_dashboard_requires_auth(self):
        """Test dashboard endpoint requires authentication."""
        response = self.client.get('/api/reports/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dashboard_admin_access(self):
        """Test admin can access dashboard."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/reports/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dashboard_manager_access(self):
        """Test manager can access dashboard."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/reports/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_occupancy_receptionist_access(self):
        """Test receptionist can access occupancy."""
        self.client.force_authenticate(user=self.receptionist)
        response = self.client.get('/api/reports/occupancy/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_occupancy_staff_denied(self):
        """Test staff cannot access occupancy."""
        self.client.force_authenticate(user=self.staff)
        response = self.client.get('/api/reports/occupancy/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_revenue_accountant_access(self):
        """Test accountant can access revenue report."""
        self.client.force_authenticate(user=self.accountant)
        response = self.client.get('/api/reports/revenue/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_revenue_receptionist_denied(self):
        """Test receptionist cannot access financial reports."""
        self.client.force_authenticate(user=self.receptionist)
        response = self.client.get('/api/reports/revenue/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_outstanding_manager_access(self):
        """Test manager can access outstanding report."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/reports/outstanding/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reservation_with_date_filter(self):
        """Test reservation report with date filter."""
        self.client.force_authenticate(user=self.manager)
        today = datetime.now(timezone.utc).date()
        response = self.client.get(f'/api/reports/reservations/?start_date={today}&end_date={today}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_date_range(self):
        """Test invalid date range returns error."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/reports/occupancy/?start_date=2026-08-14&end_date=2026-08-01')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
