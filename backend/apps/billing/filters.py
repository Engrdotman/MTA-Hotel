import django_filters

from apps.billing.models import Invoice


class InvoiceFilter(django_filters.FilterSet):
    """Filter for invoices."""
    
    invoice_number = django_filters.CharFilter(lookup_expr="icontains")
    guest_name = django_filters.CharFilter(field_name="guest__first_name", lookup_expr="icontains")
    reservation_number = django_filters.CharFilter(field_name="reservation__reservation_number", lookup_expr="icontains")
    status = django_filters.ChoiceFilter(choices=Invoice.Status.choices)
    issued_at_from = django_filters.DateTimeFilter(field_name="issued_at", lookup_expr="gte")
    issued_at_to = django_filters.DateTimeFilter(field_name="issued_at", lookup_expr="lte")

    class Meta:
        model = Invoice
        fields = ("status", "currency")
