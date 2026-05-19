from django.db.models import Count
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from delivery.models import CatalogItem, DeliveryMission, Drone
from telemetry.models import Telemetry
from .permissions import IsManager, IsOperator
from .serializers import (
    CatalogItemSerializer,
    CustomerOrderCreateSerializer,
    DroneSummarySerializer,
    MissionSummarySerializer,
    TelemetrySnapshotSerializer,
)


class HealthCheckView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({'status': 'ok', 'service': 'drone-delivery-bff'})


class CustomerDashboardBFFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        missions = DeliveryMission.objects.filter(customer=request.user).select_related('drone').order_by('-created_at')
        stores = [
            {'code': code, 'name': name}
            for code, name in CatalogItem.STORE_CHOICES
        ]
        catalog = CatalogItem.objects.order_by('store', 'name')[:40]
        return Response({
            'profile': {
                'id': request.user.id,
                'username': request.user.username,
                'phone': request.user.phone,
            },
            'stores': stores,
            'catalog_preview': CatalogItemSerializer(catalog, many=True).data,
            'missions': MissionSummarySerializer(missions, many=True).data,
        })

    def post(self, request):
        serializer = CustomerOrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        mission = serializer.save()
        return Response(MissionSummarySerializer(mission).data, status=status.HTTP_201_CREATED)


class ManagerDashboardBFFView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get(self, request):
        status_filter = request.query_params.get('status')
        missions = DeliveryMission.objects.select_related('customer', 'drone').order_by('-created_at')
        if status_filter:
            missions = missions.filter(status=status_filter)

        today = timezone.now().date()
        status_counts = DeliveryMission.objects.values('status').annotate(count=Count('id')).order_by('status')
        return Response({
            'metrics': {
                'total_drones': Drone.objects.count(),
                'ready_drones': Drone.objects.filter(status='ready').count(),
                'drones_in_air': Drone.objects.filter(status='flying').count(),
                'completed_today': DeliveryMission.objects.filter(status='completed', updated_at__date=today).count(),
                'missions_by_status': {row['status']: row['count'] for row in status_counts},
            },
            'missions': MissionSummarySerializer(missions[:100], many=True).data,
        })


class OperatorControlBFFView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOperator]

    def get(self, request):
        new_missions = DeliveryMission.objects.filter(status='new').select_related('customer', 'drone').order_by('created_at')
        ready_drones = Drone.objects.filter(status='ready').order_by('serial_number')
        latest_telemetry = Telemetry.objects.select_related('drone').order_by('-timestamp')[:20]
        return Response({
            'new_missions': MissionSummarySerializer(new_missions, many=True).data,
            'ready_drones': DroneSummarySerializer(ready_drones, many=True).data,
            'telemetry': TelemetrySnapshotSerializer(latest_telemetry, many=True).data,
        })
