from decimal import Decimal
from datetime import datetime, timedelta, timezone

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.accounts.models import Role
from apps.billing.models import Invoice, InvoiceItem, StayCharge
from apps.billing.services import InvoiceService, PaymentService
from apps.guests.models import Guest
from apps.payments.models import Payment
from apps.reservations.models import Reservation
from apps.rooms.models import Room, RoomType
from apps.stays.models import Stay

User = get_user_model()


class InvoiceServiceTestCase(TestCase):
    """Tests for invoice service."""

    def setUp(self):
        """Set up test data."""
        # Create role
        self.admin_role = Role.objects.create(name=Role.ADMIN)
        self.accountant_role = Role.objects.create(name=Role.ACCOUNTANT)

        # Create user
        self.user = User.objects.create_user(
            email="admin@test.com",
            first_name="Admin",
            last_name="User",
            password="testpass123",
            role=self.admin_role,
        )

        # Create guest
        self.guest = Guest.objects.create(
            guest_code="G001",
            first_name="John",
            last_name="Doe",
            phone="08012345678",
        )

        # Create room type
        self.room_type = RoomType.objects.create(
            name="Standard",
            capacity=2,
            base_price=Decimal("40000.00"),
        )

        # Create room
        self.room = Room.objects.create(
            room_number="101",
            room_type=self.room_type,
            floor="1",
        )

        # Create reservation
        self.check_in = datetime.now(timezone.utc).date()
        self.check_out = self.check_in + timedelta(days=3)
        self.reservation = Reservation.objects.create(
            reservation_number="RES001",
            guest=self.guest,
            room=self.room,
            check_in_date=self.check_in,
            check_out_date=self.check_out,
            adults=1,
            status=Reservation.Status.CONFIRMED,
        )

        # Create stay
        self.stay = Stay.objects.create(
            reservation=self.reservation,
            guest=self.guest,
            room=self.room,
            checked_in_at=datetime.combine(self.check_in, datetime.min.time()).replace(tzinfo=timezone.utc),
            status=Stay.Status.CHECKED_IN,
        )

    def test_generate_invoice_number(self):
        """Test invoice number generation."""
        inv_num = InvoiceService.generate_invoice_number()
        self.assertIn("INV-", inv_num)
        self.assertEqual(inv_num, "INV-000001")

    def test_invoice_number_unique(self):
        """Test that invoice numbers are unique."""
        num1 = InvoiceService.generate_invoice_number()
        Invoice.objects.create(
            invoice_number=num1,
            guest=self.guest,
            reservation=self.reservation,
            subtotal=Decimal("0"),
        )
        num2 = InvoiceService.generate_invoice_number()
        self.assertNotEqual(num1, num2)
        self.assertEqual(num2, "INV-000002")

    def test_calculate_room_charges(self):
        """Test room charge calculation."""
        nights, rate, charge = InvoiceService.calculate_room_charges(self.stay)
        self.assertEqual(nights, 3)
        self.assertEqual(rate, Decimal("40000.00"))
        self.assertEqual(charge, Decimal("120000.00"))

    def test_create_invoice_basic(self):
        """Test basic invoice creation."""
        invoice = InvoiceService.create_invoice_for_stay(
            stay=self.stay,
            created_by=self.user,
        )
        self.assertIsNotNone(invoice.id)
        self.assertEqual(invoice.status, Invoice.Status.DRAFT)
        self.assertEqual(invoice.subtotal, Decimal("120000.00"))
        self.assertEqual(invoice.total, Decimal("120000.00"))
        self.assertEqual(invoice.balance, Decimal("120000.00"))
        self.assertEqual(invoice.amount_paid, Decimal("0"))

    def test_create_invoice_with_discount(self):
        """Test invoice creation with discount."""
        discount = Decimal("10000.00")
        invoice = InvoiceService.create_invoice_for_stay(
            stay=self.stay,
            discount=discount,
            created_by=self.user,
        )
        self.assertEqual(invoice.discount, discount)
        self.assertEqual(invoice.total, Decimal("110000.00"))
        self.assertEqual(invoice.balance, Decimal("110000.00"))

    def test_create_invoice_duplicate_prevented(self):
        """Test that duplicate invoices are prevented."""
        InvoiceService.create_invoice_for_stay(
            stay=self.stay,
            created_by=self.user,
        )
        with self.assertRaises(ValueError) as cm:
            InvoiceService.create_invoice_for_stay(
                stay=self.stay,
                created_by=self.user,
            )
        self.assertIn("already exists", str(cm.exception))

    def test_issue_invoice(self):
        """Test issuing an invoice."""
        invoice = InvoiceService.create_invoice_for_stay(
            stay=self.stay,
            created_by=self.user,
        )
        self.assertEqual(invoice.status, Invoice.Status.DRAFT)

        invoice = InvoiceService.issue_invoice(invoice)
        self.assertEqual(invoice.status, Invoice.Status.ISSUED)
        self.assertIsNotNone(invoice.issued_at)

    def test_void_invoice(self):
        """Test voiding an invoice."""
        invoice = InvoiceService.create_invoice_for_stay(
            stay=self.stay,
            created_by=self.user,
        )
        invoice = InvoiceService.void_invoice(invoice)
        self.assertEqual(invoice.status, Invoice.Status.VOID)

    def test_invoice_items_created(self):
        """Test that invoice items are created correctly."""
        invoice = InvoiceService.create_invoice_for_stay(
            stay=self.stay,
            created_by=self.user,
        )
        items = invoice.items.all()
        self.assertEqual(items.count(), 1)

        item = items.first()
        self.assertEqual(item.item_type, InvoiceItem.ItemType.ROOM)
        self.assertEqual(item.quantity, Decimal("3"))
        self.assertEqual(item.unit_price, Decimal("40000.00"))
        self.assertEqual(item.amount, Decimal("120000.00"))

    def test_create_invoice_includes_pending_stay_charges(self):
        """Pending stay charges are added to the invoice and marked invoiced."""
        charge = StayCharge.objects.create(
            stay=self.stay,
            charge_type=StayCharge.ChargeType.LAUNDRY,
            description="Laundry service",
            quantity=Decimal("2"),
            unit_price=Decimal("2500.00"),
            service_date=self.check_in,
            created_by=self.user,
        )

        invoice = InvoiceService.create_invoice_for_stay(
            stay=self.stay,
            created_by=self.user,
        )

        charge.refresh_from_db()
        self.assertEqual(invoice.subtotal, Decimal("125000.00"))
        self.assertEqual(invoice.total, Decimal("125000.00"))
        self.assertEqual(invoice.items.count(), 2)
        self.assertTrue(invoice.items.filter(description="Laundry service", amount=Decimal("5000.00")).exists())
        self.assertEqual(charge.status, StayCharge.Status.INVOICED)
        self.assertEqual(charge.invoice, invoice)


class PaymentServiceTestCase(TestCase):
    """Tests for payment service."""

    def setUp(self):
        """Set up test data."""
        # Create role
        self.admin_role = Role.objects.create(name=Role.ADMIN)

        # Create user
        self.user = User.objects.create_user(
            email="admin@test.com",
            first_name="Admin",
            last_name="User",
            password="testpass123",
            role=self.admin_role,
        )

        # Create guest
        self.guest = Guest.objects.create(
            guest_code="G001",
            first_name="John",
            last_name="Doe",
        )

        # Create reservation
        self.reservation = Reservation.objects.create(
            reservation_number="RES001",
            guest=self.guest,
            room=Room.objects.create(
                room_number="101",
                room_type=RoomType.objects.create(
                    name="Standard",
                    capacity=2,
                    base_price=Decimal("40000.00"),
                ),
            ),
            check_in_date=datetime.now(timezone.utc).date(),
            check_out_date=(datetime.now(timezone.utc) + timedelta(days=3)).date(),
        )

        # Create invoice
        self.invoice = Invoice.objects.create(
            invoice_number="INV-000001",
            guest=self.guest,
            reservation=self.reservation,
            status=Invoice.Status.ISSUED,
            subtotal=Decimal("120000.00"),
            total=Decimal("120000.00"),
            amount_paid=Decimal("0"),
            balance=Decimal("120000.00"),
            created_by=self.user,
        )

    def test_generate_payment_reference(self):
        """Test payment reference generation."""
        ref = PaymentService.generate_payment_reference()
        self.assertIn("PAY-", ref)
        self.assertEqual(ref, "PAY-000001")

    def test_payment_reference_unique(self):
        """Test that payment references are unique."""
        ref1 = PaymentService.generate_payment_reference()
        Payment.objects.create(
            payment_reference=ref1,
            invoice=self.invoice,
            amount=Decimal("50000.00"),
            method=Payment.Method.CASH,
            received_by=self.user,
        )
        ref2 = PaymentService.generate_payment_reference()
        self.assertNotEqual(ref1, ref2)
        self.assertEqual(ref2, "PAY-000002")

    def test_record_payment_full(self):
        """Test recording a full payment."""
        payment = PaymentService.record_payment(
            invoice=self.invoice,
            amount=Decimal("120000.00"),
            method=Payment.Method.CASH,
            received_by=self.user,
        )
        self.assertIsNotNone(payment.id)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.amount_paid, Decimal("120000.00"))
        self.assertEqual(self.invoice.balance, Decimal("0"))
        self.assertEqual(self.invoice.status, Invoice.Status.PAID)

    def test_record_payment_partial(self):
        """Test recording a partial payment."""
        payment = PaymentService.record_payment(
            invoice=self.invoice,
            amount=Decimal("50000.00"),
            method=Payment.Method.CASH,
            received_by=self.user,
        )
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.amount_paid, Decimal("50000.00"))
        self.assertEqual(self.invoice.balance, Decimal("70000.00"))
        self.assertEqual(self.invoice.status, Invoice.Status.PARTIALLY_PAID)

    def test_record_payment_multiple(self):
        """Test recording multiple payments."""
        PaymentService.record_payment(
            invoice=self.invoice,
            amount=Decimal("50000.00"),
            method=Payment.Method.CASH,
            received_by=self.user,
        )
        PaymentService.record_payment(
            invoice=self.invoice,
            amount=Decimal("70000.00"),
            method=Payment.Method.BANK_TRANSFER,
            received_by=self.user,
        )
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.amount_paid, Decimal("120000.00"))
        self.assertEqual(self.invoice.balance, Decimal("0"))
        self.assertEqual(self.invoice.payments.count(), 2)

    def test_record_payment_overpayment_rejected(self):
        """Test that overpayment is rejected."""
        with self.assertRaises(ValueError) as cm:
            PaymentService.record_payment(
                invoice=self.invoice,
                amount=Decimal("150000.00"),
                method=Payment.Method.CASH,
                received_by=self.user,
            )
        self.assertIn("exceeds balance", str(cm.exception))

    def test_record_payment_negative_rejected(self):
        """Test that negative payment is rejected."""
        with self.assertRaises(ValueError) as cm:
            PaymentService.record_payment(
                invoice=self.invoice,
                amount=Decimal("-10000.00"),
                method=Payment.Method.CASH,
                received_by=self.user,
            )
        self.assertIn("greater than 0", str(cm.exception))

    def test_record_payment_zero_rejected(self):
        """Test that zero payment is rejected."""
        with self.assertRaises(ValueError) as cm:
            PaymentService.record_payment(
                invoice=self.invoice,
                amount=Decimal("0"),
                method=Payment.Method.CASH,
                received_by=self.user,
            )
        self.assertIn("greater than 0", str(cm.exception))


class InvoiceAPITestCase(APITestCase):
    """Tests for invoice API endpoints."""

    def setUp(self):
        """Set up test data."""
        # Create roles
        self.admin_role = Role.objects.create(name=Role.ADMIN)
        self.receptionist_role = Role.objects.create(name=Role.RECEPTIONIST)
        self.staff_role = Role.objects.create(name=Role.STAFF)

        # Create users
        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            first_name="Admin",
            last_name="User",
            password="testpass123",
            role=self.admin_role,
        )
        self.receptionist_user = User.objects.create_user(
            email="receptionist@test.com",
            first_name="Receptionist",
            last_name="User",
            password="testpass123",
            role=self.receptionist_role,
        )
        self.staff_user = User.objects.create_user(
            email="staff@test.com",
            first_name="Staff",
            last_name="User",
            password="testpass123",
            role=self.staff_role,
        )

        # Create guest
        self.guest = Guest.objects.create(
            guest_code="G001",
            first_name="John",
            last_name="Doe",
            phone="08012345678",
        )

        # Create room
        self.room_type = RoomType.objects.create(
            name="Standard",
            capacity=2,
            base_price=Decimal("40000.00"),
        )
        self.room = Room.objects.create(
            room_number="101",
            room_type=self.room_type,
        )

        # Create reservation
        self.check_in = datetime.now(timezone.utc).date()
        self.check_out = self.check_in + timedelta(days=3)
        self.reservation = Reservation.objects.create(
            reservation_number="RES001",
            guest=self.guest,
            room=self.room,
            check_in_date=self.check_in,
            check_out_date=self.check_out,
        )

        # Create stay
        self.stay = Stay.objects.create(
            reservation=self.reservation,
            guest=self.guest,
            room=self.room,
            checked_in_at=datetime.combine(self.check_in, datetime.min.time()).replace(tzinfo=timezone.utc),
        )

        self.client = APIClient()

    def test_create_invoice_requires_auth(self):
        """Test that creating invoice requires authentication."""
        response = self.client.post("/api/billing/invoices/", {"stay_id": self.stay.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_invoice_admin_allowed(self):
        """Test that admin can create invoice."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post("/api/billing/invoices/", {"stay_id": self.stay.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_charge_and_create_invoice_from_api(self):
        """Test that API-created charges flow into generated invoices."""
        self.client.force_authenticate(user=self.admin_user)
        charge_response = self.client.post(
            "/api/billing/charges/",
            {
                "stay": self.stay.id,
                "charge_type": StayCharge.ChargeType.FOOD,
                "description": "Restaurant order",
                "quantity": "1.00",
                "unit_price": "7500.00",
                "service_date": self.check_in.isoformat(),
            },
        )
        self.assertEqual(charge_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(charge_response.data["amount"]), Decimal("7500.00"))

        invoice_response = self.client.post("/api/billing/invoices/", {"stay_id": self.stay.id})
        self.assertEqual(invoice_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(invoice_response.data["subtotal"]), Decimal("127500.00"))
        self.assertEqual(len(invoice_response.data["stay_charges"]), 1)

    def test_cannot_add_charge_after_invoice_exists(self):
        """Charges cannot be added to a stay once an active invoice exists."""
        self.client.force_authenticate(user=self.admin_user)
        InvoiceService.create_invoice_for_stay(stay=self.stay, created_by=self.admin_user)
        response = self.client.post(
            "/api/billing/charges/",
            {
                "stay": self.stay.id,
                "charge_type": StayCharge.ChargeType.OTHER,
                "description": "Late fee",
                "quantity": "1.00",
                "unit_price": "1000.00",
                "service_date": self.check_in.isoformat(),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invoice_staff_denied(self):
        """Test that staff cannot create invoice."""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post("/api/billing/invoices/", {"stay_id": self.stay.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_invoices_pagination(self):
        """Test listing invoices with pagination."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/billing/invoices/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, (list, dict))
