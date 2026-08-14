from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.reports.services import ReportService
from apps.reports.serializers import (
    DashboardSummarySerializer,
    OccupancyReportSerializer,
    ReservationReportSerializer,
    RevenueReportSerializer,
    OutstandingReportSerializer,
    DateRangeFilterSerializer,
)
from apps.reports.permissions import (
    CanAccessReports,
    CanAccessFinancialReports,
    CanAccessOperationalReports,
)


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanAccessReports])
def dashboard_summary(request):
    """Get dashboard summary with real-time data.
    
    GET /api/reports/dashboard/
    """
    try:
        data = ReportService.get_dashboard_summary()
        serializer = DashboardSummarySerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanAccessOperationalReports])
def occupancy_report(request):
    """Get occupancy report.
    
    GET /api/reports/occupancy/
    Query params:
      - date: YYYY-MM-DD (optional, defaults to today)
      - start_date: YYYY-MM-DD (optional)
      - end_date: YYYY-MM-DD (optional)
    """
    try:
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        date = request.query_params.get('date')

        # If date is provided, use it for both start and end
        if date:
            start_date = date
            end_date = date

        # Validate dates if provided
        filter_serializer = DateRangeFilterSerializer(data={
            'start_date': start_date,
            'end_date': end_date,
        })
        if not filter_serializer.is_valid():
            return Response(
                filter_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse dates
        validated_data = filter_serializer.validated_data
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')

        data = ReportService.get_occupancy_report(start_date, end_date)
        serializer = OccupancyReportSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanAccessOperationalReports])
def reservation_report(request):
    """Get reservation report.
    
    GET /api/reports/reservations/
    Query params:
      - start_date: YYYY-MM-DD (optional, defaults to today)
      - end_date: YYYY-MM-DD (optional, defaults to today)
      - status: Status filter (optional)
    """
    try:
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status_filter = request.query_params.get('status')

        # Validate dates if provided
        filter_serializer = DateRangeFilterSerializer(data={
            'start_date': start_date,
            'end_date': end_date,
        })
        if not filter_serializer.is_valid():
            return Response(
                filter_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse dates
        validated_data = filter_serializer.validated_data
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')

        data = ReportService.get_reservation_report(start_date, end_date, status_filter)
        serializer = ReservationReportSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanAccessFinancialReports])
def revenue_report(request):
    """Get revenue report based on actual payments received.
    
    GET /api/reports/revenue/
    Query params:
      - start_date: YYYY-MM-DD (optional, defaults to today)
      - end_date: YYYY-MM-DD (optional, defaults to today)
    """
    try:
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Validate dates if provided
        filter_serializer = DateRangeFilterSerializer(data={
            'start_date': start_date,
            'end_date': end_date,
        })
        if not filter_serializer.is_valid():
            return Response(
                filter_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse dates
        validated_data = filter_serializer.validated_data
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')

        data = ReportService.get_revenue_report(start_date, end_date)
        serializer = RevenueReportSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanAccessFinancialReports])
def outstanding_report(request):
    """Get outstanding balances report.
    
    GET /api/reports/outstanding/
    Query params:
      - start_date: YYYY-MM-DD (optional)
      - end_date: YYYY-MM-DD (optional)
    """
    try:
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Validate dates if provided
        filter_serializer = DateRangeFilterSerializer(data={
            'start_date': start_date,
            'end_date': end_date,
        })
        if not filter_serializer.is_valid():
            return Response(
                filter_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse dates
        validated_data = filter_serializer.validated_data
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')

        data = ReportService.get_outstanding_report(start_date, end_date)
        serializer = OutstandingReportSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
