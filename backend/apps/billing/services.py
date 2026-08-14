from decimal import Decimal
from datetime import datetime, timezone

from django.db import transaction

from apps.billing.models import Invoice, InvoiceItem
from apps.payments.models import Payment
from apps.stays.models import Stay


class InvoiceService:
    """Service for invoice operations."""

    INVOICE_PREFIX = "INV"
    MAX_INVOICE_NUMBER = 999999

    @staticmethod
    def generate_invoice_number():
        """Generate a unique invoice number.
        
        Format: INV-000001
        """
        latest_invoice = Invoice.objects.order_by("-created_at").first()
        
        if not latest_invoice:
            number = 1
        else:
            # Extract the numeric part from the invoice number
            try:
                numeric_part = int(latest_invoice.invoice_number.split("-")[-1])
                number = numeric_part + 1
            except (ValueError, IndexError):
                number = 1
        
        if number > InvoiceService.MAX_INVOICE_NUMBER:
            raise ValueError("Invoice number overflow")
        
        return f"{InvoiceService.INVOICE_PREFIX}-{number:06d}"

    @staticmethod
    def calculate_room_charges(stay):
        """Calculate room charges based on stay dates and room rate.
        
        Returns: (number_of_nights, room_rate, total_charge)
        """
        if stay.checked_out_at:
            check_in = stay.checked_in_at
            check_out = stay.checked_out_at
        else:
            # If not checked out, calculate based on reservation dates
            check_in = stay.reservation.check_in_date
            check_out = stay.reservation.check_out_date
        
        # Calculate number of nights
        nights = (check_out.date() - check_in.date()).days
        if nights <= 0:
            nights = 1
        
        # Get room rate from room type
        room_rate = stay.room.room_type.base_price
        
        # Calculate total charge
        total_charge = Decimal(nights) * room_rate
        
        return nights, room_rate, total_charge

    @staticmethod
    @transaction.atomic
    def create_invoice_for_stay(stay, discount=None, created_by=None):
        """Create an invoice for a stay with room charges.
        
        Args:
            stay: Stay instance
            discount: Optional discount amount
            created_by: User who created the invoice
            
        Returns:
            Invoice instance
        """
        # Check if invoice already exists for this stay
        existing_invoice = Invoice.objects.filter(stay=stay).exclude(status=Invoice.Status.VOID).first()
        if existing_invoice:
            raise ValueError(f"Invoice already exists for this stay: {existing_invoice.invoice_number}")
        
        # Calculate room charges
        nights, room_rate, room_charge = InvoiceService.calculate_room_charges(stay)
        
        # Initialize amounts
        subtotal = room_charge
        discount_amount = Decimal("0")
        
        if discount and discount > 0:
            # Validate discount
            if discount > subtotal:
                raise ValueError("Discount cannot exceed subtotal")
            discount_amount = Decimal(str(discount))
        
        # Tax (for MVP, defaulting to 0)
        tax = Decimal("0")
        
        # Calculate total
        total_amount = subtotal - discount_amount + tax
        
        # Generate invoice number
        invoice_number = InvoiceService.generate_invoice_number()
        
        # Create invoice
        invoice = Invoice.objects.create(
            invoice_number=invoice_number,
            stay=stay,
            guest=stay.guest,
            reservation=stay.reservation,
            status=Invoice.Status.DRAFT,
            subtotal=subtotal,
            discount=discount_amount,
            tax=tax,
            total=total_amount,
            amount_paid=Decimal("0"),
            balance=total_amount,
            created_by=created_by,
        )
        
        # Create room charge line item
        InvoiceItem.objects.create(
            invoice=invoice,
            item_type=InvoiceItem.ItemType.ROOM,
            description=f"Room {stay.room.room_number} - {nights} night(s) × ₦{room_rate}",
            quantity=Decimal(nights),
            unit_price=room_rate,
            amount=room_charge,
            service_date=stay.checked_in_at.date(),
        )
        
        return invoice

    @staticmethod
    def issue_invoice(invoice):
        """Issue a draft invoice.
        
        Changes status from DRAFT to ISSUED.
        """
        if invoice.status != Invoice.Status.DRAFT:
            raise ValueError(f"Can only issue draft invoices. Current status: {invoice.status}")
        
        invoice.status = Invoice.Status.ISSUED
        invoice.issued_at = datetime.now(timezone.utc)
        invoice.save()
        return invoice

    @staticmethod
    def void_invoice(invoice):
        """Void an invoice.
        
        Only void unpaid or partially paid invoices.
        """
        if invoice.status in (Invoice.Status.PAID, Invoice.Status.VOID):
            raise ValueError(f"Cannot void invoice with status: {invoice.status}")
        
        invoice.status = Invoice.Status.VOID
        invoice.save()
        return invoice


class PaymentService:
    """Service for payment operations."""

    PAYMENT_PREFIX = "PAY"
    MAX_PAYMENT_NUMBER = 999999

    @staticmethod
    def generate_payment_reference():
        """Generate a unique payment reference.
        
        Format: PAY-000001
        """
        latest_payment = Payment.objects.order_by("-created_at").first()
        
        if not latest_payment:
            number = 1
        else:
            # Extract the numeric part from the payment reference
            try:
                numeric_part = int(latest_payment.payment_reference.split("-")[-1])
                number = numeric_part + 1
            except (ValueError, IndexError):
                number = 1
        
        if number > PaymentService.MAX_PAYMENT_NUMBER:
            raise ValueError("Payment reference overflow")
        
        return f"{PaymentService.PAYMENT_PREFIX}-{number:06d}"

    @staticmethod
    @transaction.atomic
    def record_payment(invoice, amount, method, received_by=None, notes=""):
        """Record a payment against an invoice.
        
        Args:
            invoice: Invoice instance
            amount: Payment amount in Decimal
            method: Payment method
            received_by: User who received the payment
            notes: Additional notes
            
        Returns:
            Payment instance
        """
        amount = Decimal(str(amount))
        
        # Validate invoice
        if invoice.status in (Invoice.Status.DRAFT, Invoice.Status.VOID):
            raise ValueError(f"Cannot record payment for {invoice.status} invoice")
        
        # Validate amount
        if amount <= 0:
            raise ValueError("Payment amount must be greater than 0")
        
        if amount > invoice.balance:
            raise ValueError(f"Payment amount {amount} exceeds balance due {invoice.balance}")
        
        # Generate payment reference
        payment_reference = PaymentService.generate_payment_reference()
        
        # Create payment
        payment = Payment.objects.create(
            payment_reference=payment_reference,
            invoice=invoice,
            amount=amount,
            method=method,
            payment_date=datetime.now(timezone.utc),
            received_by=received_by,
            notes=notes,
        )
        
        # Update invoice
        invoice.amount_paid += amount
        invoice.balance -= amount
        
        # Update invoice status
        if invoice.balance == 0:
            invoice.status = Invoice.Status.PAID
        elif invoice.balance > 0 and invoice.amount_paid > 0:
            invoice.status = Invoice.Status.PARTIALLY_PAID
        
        invoice.save()
        
        return payment

    @staticmethod
    def get_invoice_summary(invoice):
        """Get a summary of an invoice with payment history.
        
        Returns a dictionary with invoice and payment details.
        """
        payments = invoice.payments.all().order_by("-payment_date")
        
        return {
            "invoice_number": invoice.invoice_number,
            "guest_name": f"{invoice.guest.first_name} {invoice.guest.last_name}",
            "room_number": invoice.stay.room.room_number if invoice.stay else "N/A",
            "status": invoice.get_status_display(),
            "subtotal": float(invoice.subtotal),
            "discount": float(invoice.discount),
            "tax": float(invoice.tax),
            "total": float(invoice.total),
            "amount_paid": float(invoice.amount_paid),
            "balance": float(invoice.balance),
            "issued_at": invoice.issued_at,
            "due_at": invoice.due_at,
            "payment_history": [
                {
                    "reference": p.payment_reference,
                    "amount": float(p.amount),
                    "method": p.get_method_display(),
                    "date": p.payment_date,
                    "received_by": p.received_by.email if p.received_by else "N/A",
                }
                for p in payments
            ],
        }
