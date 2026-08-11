from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.guests.models import Guest
from apps.reservations.models import Reservation
from apps.rooms.models import Room, RoomType

from .models import Invoice, InvoiceItem


class BillingModelTests(TestCase):
    def setUp(self):
        room_type = RoomType.objects.create(name="Standard", capacity=2, base_price="100.00")
        room = Room.objects.create(room_number="101", room_type=room_type)
        self.guest = Guest.objects.create(guest_code="G001", first_name="Ada", last_name="Lovelace")
        self.reservation = Reservation.objects.create(
            reservation_number="R001",
            guest=self.guest,
            room=room,
            check_in_date="2026-08-11",
            check_out_date="2026-08-12",
            adults=1,
        )

    def test_invoice_number_is_unique(self):
        Invoice.objects.create(invoice_number="INV001", guest=self.guest, reservation=self.reservation)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Invoice.objects.create(invoice_number="INV001", guest=self.guest, reservation=self.reservation)

    def test_invoice_rejects_negative_money(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Invoice.objects.create(
                invoice_number="INV001",
                guest=self.guest,
                reservation=self.reservation,
                total="-1.00",
            )

    def test_invoice_item_requires_positive_quantity(self):
        invoice = Invoice.objects.create(invoice_number="INV001", guest=self.guest, reservation=self.reservation)

        with self.assertRaises(IntegrityError), transaction.atomic():
            InvoiceItem.objects.create(
                invoice=invoice,
                item_type=InvoiceItem.ItemType.ROOM,
                description="Room charge",
                quantity="0.00",
                unit_price="100.00",
                amount="0.00",
            )
