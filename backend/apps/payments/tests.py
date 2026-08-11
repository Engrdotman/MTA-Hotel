from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.billing.models import Invoice
from apps.guests.models import Guest
from apps.reservations.models import Reservation
from apps.rooms.models import Room, RoomType

from .models import Payment


class PaymentModelTests(TestCase):
    def setUp(self):
        room_type = RoomType.objects.create(name="Standard", capacity=2, base_price="100.00")
        room = Room.objects.create(room_number="101", room_type=room_type)
        guest = Guest.objects.create(guest_code="G001", first_name="Ada", last_name="Lovelace")
        reservation = Reservation.objects.create(
            reservation_number="R001",
            guest=guest,
            room=room,
            check_in_date="2026-08-11",
            check_out_date="2026-08-12",
            adults=1,
        )
        self.invoice = Invoice.objects.create(invoice_number="INV001", guest=guest, reservation=reservation)

    def test_payment_reference_is_unique(self):
        Payment.objects.create(
            payment_reference="PAY001",
            invoice=self.invoice,
            amount="10.00",
            method=Payment.Method.CASH,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            Payment.objects.create(
                payment_reference="PAY001",
                invoice=self.invoice,
                amount="10.00",
                method=Payment.Method.CASH,
            )

    def test_payment_amount_must_be_positive(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Payment.objects.create(
                payment_reference="PAY001",
                invoice=self.invoice,
                amount="0.00",
                method=Payment.Method.CASH,
            )
