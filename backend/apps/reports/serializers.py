from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    """Serializer for dashboard summary data."""
    
    total_rooms = serializers.IntegerField()
    available_rooms = serializers.IntegerField()
    occupied_rooms = serializers.IntegerField()
    reserved_rooms = serializers.IntegerField()
    maintenance_rooms = serializers.IntegerField()
    out_of_service_rooms = serializers.IntegerField()
    dirty_rooms = serializers.IntegerField()
    today_check_ins = serializers.IntegerField()
    today_check_outs = serializers.IntegerField()
    current_guests = serializers.IntegerField()
    today_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    outstanding_balance = serializers.DecimalField(max_digits=12, decimal_places=2)


class OccupancyReportSerializer(serializers.Serializer):
    """Serializer for occupancy report."""
    
    date_range = serializers.DictField()
    total_rooms = serializers.IntegerField()
    occupied = serializers.IntegerField()
    available = serializers.IntegerField()
    reserved = serializers.IntegerField()
    maintenance = serializers.IntegerField()
    out_of_service = serializers.IntegerField()
    dirty = serializers.IntegerField()
    occupancy_rate = serializers.CharField()


class ReservationReportSerializer(serializers.Serializer):
    """Serializer for reservation report."""
    
    date_range = serializers.DictField()
    total = serializers.IntegerField()
    pending = serializers.IntegerField()
    confirmed = serializers.IntegerField()
    checked_in = serializers.IntegerField()
    checked_out = serializers.IntegerField()
    cancelled = serializers.IntegerField()
    no_show = serializers.IntegerField()


class RevenueReportSerializer(serializers.Serializer):
    """Serializer for revenue report."""
    
    date_range = serializers.DictField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    cash = serializers.DecimalField(max_digits=12, decimal_places=2)
    pos = serializers.DecimalField(max_digits=12, decimal_places=2)
    bank_transfer = serializers.DecimalField(max_digits=12, decimal_places=2)
    other = serializers.DecimalField(max_digits=12, decimal_places=2)


class OutstandingReportSerializer(serializers.Serializer):
    """Serializer for outstanding balances report."""
    
    date_range = serializers.DictField()
    total_outstanding = serializers.DecimalField(max_digits=12, decimal_places=2)
    unpaid_invoices = serializers.IntegerField()
    partially_paid_invoices = serializers.IntegerField()


class DateRangeFilterSerializer(serializers.Serializer):
    """Serializer for date range filtering."""
    
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # If both dates provided, validate range
        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError("start_date must be <= end_date")

        return data
