from decimal import Decimal
from datetime import datetime, timedelta, timezone
from django.db.models import Q, Count, Sum, Case, When, DecimalField
from django.utils import timezone as django_timezone

from apps.rooms.models import Room, RoomType
from apps.reservations.models import Reservation
from apps.stays.models import Stay
from apps.billing.models import Invoice
from apps.payments.models import Payment


class ReportService:
    """Service for generating hotel reports."""

    @staticmethod
    def get_dashboard_summary():
        """Get real-time dashboard summary.
        
        Returns dictionary with:
        - Room counts by status
        - Today's check-ins and check-outs
        - Current guests
        - Today's revenue
        - Outstanding balance
        """
        now = django_timezone.now()
        today = now.date()

        # Room counts by status
        total_rooms = Room.objects.count()
        room_statuses = Room.objects.values('status').annotate(count=Count('id'))
        status_counts = {item['status']: item['count'] for item in room_statuses}

        # Today's check-ins (stays that started today)
        today_checkins = Stay.objects.filter(
            checked_in_at__date=today
        ).count()

        # Today's check-outs (stays that ended today)
        today_checkouts = Stay.objects.filter(
            checked_out_at__date=today
        ).count()

        # Current guests (active stays)
        current_guests = Stay.objects.filter(
            status=Stay.Status.CHECKED_IN
        ).count()

        # Today's revenue (payments recorded today)
        today_revenue = Payment.objects.filter(
            created_at__date=today
        ).aggregate(total=Sum('amount', output_field=DecimalField()))['total'] or Decimal('0')

        # Outstanding balance (sum of all invoice balances)
        outstanding = Invoice.objects.aggregate(
            total=Sum('balance', output_field=DecimalField())
        )['total'] or Decimal('0')

        return {
            'total_rooms': total_rooms,
            'available_rooms': status_counts.get(Room.Status.AVAILABLE, 0),
            'occupied_rooms': status_counts.get(Room.Status.OCCUPIED, 0),
            'reserved_rooms': status_counts.get(Room.Status.RESERVED, 0),
            'maintenance_rooms': status_counts.get(Room.Status.MAINTENANCE, 0),
            'out_of_service_rooms': status_counts.get(Room.Status.OUT_OF_SERVICE, 0),
            'dirty_rooms': status_counts.get(Room.Status.DIRTY, 0),
            'today_check_ins': today_checkins,
            'today_check_outs': today_checkouts,
            'current_guests': current_guests,
            'today_revenue': str(today_revenue),
            'outstanding_balance': str(outstanding),
        }

    @staticmethod
    def get_occupancy_report(start_date=None, end_date=None):
        """Get occupancy report for date range.
        
        If no dates provided, uses today.
        
        Returns:
        - Total rooms
        - Room status counts
        - Occupancy rate
        """
        if not start_date:
            start_date = django_timezone.now().date()
        if not end_date:
            end_date = start_date

        # Validate date range
        if start_date > end_date:
            raise ValueError("start_date must be <= end_date")

        total_rooms = Room.objects.count()

        # Get room counts by status
        room_statuses = Room.objects.values('status').annotate(count=Count('id'))
        status_counts = {item['status']: item['count'] for item in room_statuses}

        occupied = status_counts.get(Room.Status.OCCUPIED, 0)
        available = status_counts.get(Room.Status.AVAILABLE, 0)
        reserved = status_counts.get(Room.Status.RESERVED, 0)
        maintenance = status_counts.get(Room.Status.MAINTENANCE, 0)
        out_of_service = status_counts.get(Room.Status.OUT_OF_SERVICE, 0)
        dirty = status_counts.get(Room.Status.DIRTY, 0)

        # Calculate occupancy rate
        if total_rooms > 0:
            occupancy_rate = Decimal(occupied) / Decimal(total_rooms) * Decimal('100')
            occupancy_rate = occupancy_rate.quantize(Decimal('0.01'))
        else:
            occupancy_rate = Decimal('0')

        return {
            'date_range': {
                'start_date': str(start_date),
                'end_date': str(end_date),
            },
            'total_rooms': total_rooms,
            'occupied': occupied,
            'available': available,
            'reserved': reserved,
            'maintenance': maintenance,
            'out_of_service': out_of_service,
            'dirty': dirty,
            'occupancy_rate': str(occupancy_rate),
        }

    @staticmethod
    def get_reservation_report(start_date=None, end_date=None, status_filter=None):
        """Get reservation report.
        
        Counts reservations by status within date range.
        """
        if not start_date:
            start_date = django_timezone.now().date()
        if not end_date:
            end_date = start_date

        # Validate date range
        if start_date > end_date:
            raise ValueError("start_date must be <= end_date")

        # Build query
        query = Reservation.objects.filter(
            check_in_date__lte=end_date,
            check_out_date__gte=start_date,
        )

        if status_filter:
            query = query.filter(status=status_filter)

        # Count by status
        status_counts = query.values('status').annotate(count=Count('id'))
        counts_dict = {item['status']: item['count'] for item in status_counts}

        total = query.count()

        return {
            'date_range': {
                'start_date': str(start_date),
                'end_date': str(end_date),
            },
            'total': total,
            'pending': counts_dict.get(Reservation.Status.PENDING, 0),
            'confirmed': counts_dict.get(Reservation.Status.CONFIRMED, 0),
            'checked_in': counts_dict.get(Reservation.Status.CHECKED_IN, 0),
            'checked_out': counts_dict.get(Reservation.Status.CHECKED_OUT, 0),
            'cancelled': counts_dict.get(Reservation.Status.CANCELLED, 0),
            'no_show': counts_dict.get(Reservation.Status.NO_SHOW, 0),
        }

    @staticmethod
    def get_revenue_report(start_date=None, end_date=None):
        """Get revenue report based on ACTUAL PAYMENTS received.
        
        Revenue = Payments received, not invoices issued.
        """
        if not start_date:
            start_date = django_timezone.now().date()
        if not end_date:
            end_date = start_date

        # Validate date range
        if start_date > end_date:
            raise ValueError("start_date must be <= end_date")

        # Convert dates to datetimes for filtering
        start_datetime = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_datetime = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)

        # Query payments within date range
        payments = Payment.objects.filter(
            created_at__gte=start_datetime,
            created_at__lte=end_datetime,
        )

        # Total revenue
        total_revenue = payments.aggregate(total=Sum('amount', output_field=DecimalField()))['total'] or Decimal('0')

        # Revenue by payment method
        method_breakdown = payments.values('method').annotate(
            total=Sum('amount', output_field=DecimalField())
        )
        method_dict = {item['method']: item['total'] for item in method_breakdown}

        return {
            'date_range': {
                'start_date': str(start_date),
                'end_date': str(end_date),
            },
            'total_revenue': str(total_revenue),
            'cash': str(method_dict.get(Payment.Method.CASH, Decimal('0'))),
            'pos': str(method_dict.get(Payment.Method.POS, Decimal('0'))),
            'bank_transfer': str(method_dict.get(Payment.Method.BANK_TRANSFER, Decimal('0'))),
            'other': str(method_dict.get(Payment.Method.OTHER, Decimal('0'))),
        }

    @staticmethod
    def get_outstanding_report(start_date=None, end_date=None):
        """Get outstanding balances report.
        
        Returns total outstanding balance and invoice counts.
        """
        # Query unpaid and partially paid invoices
        invoices = Invoice.objects.exclude(status=Invoice.Status.VOID)

        if start_date and end_date:
            # Validate date range
            if start_date > end_date:
                raise ValueError("start_date must be <= end_date")

            # Convert to datetimes
            start_datetime = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_datetime = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)

            # Filter by issued date
            invoices = invoices.filter(
                issued_at__gte=start_datetime,
                issued_at__lte=end_datetime,
            )

        # Total outstanding balance
        total_outstanding = invoices.aggregate(
            total=Sum('balance', output_field=DecimalField())
        )['total'] or Decimal('0')

        # Count unpaid and partially paid
        unpaid_count = invoices.filter(status=Invoice.Status.ISSUED).count()
        partially_paid_count = invoices.filter(status=Invoice.Status.PARTIALLY_PAID).count()

        return {
            'date_range': {
                'start_date': str(start_date) if start_date else None,
                'end_date': str(end_date) if end_date else None,
            },
            'total_outstanding': str(total_outstanding),
            'unpaid_invoices': unpaid_count,
            'partially_paid_invoices': partially_paid_count,
        }
