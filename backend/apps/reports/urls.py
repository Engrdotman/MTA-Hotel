from django.urls import path

from apps.reports.views import (
    dashboard_summary,
    occupancy_report,
    reservation_report,
    revenue_report,
    outstanding_report,
)

urlpatterns = [
    path('dashboard/', dashboard_summary, name='dashboard-summary'),
    path('occupancy/', occupancy_report, name='occupancy-report'),
    path('reservations/', reservation_report, name='reservation-report'),
    path('revenue/', revenue_report, name='revenue-report'),
    path('outstanding/', outstanding_report, name='outstanding-report'),
]
