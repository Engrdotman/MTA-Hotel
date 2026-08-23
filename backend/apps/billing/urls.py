from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.billing.views import InvoiceViewSet, StayChargeViewSet

router = DefaultRouter()
router.register("invoices", InvoiceViewSet, basename="invoice")
router.register("charges", StayChargeViewSet, basename="stay-charge")

urlpatterns = [
    path("", include(router.urls)),
]

