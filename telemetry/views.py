from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from delivery.models import Drone, DeliveryMission
from .models import Telemetry
from .serializers import WebTelemetrySerializer, MobileTelemetrySerializer

class LatestTelemetryView(APIView):
    permission_classes = [permissions.AllowAny] # For demo purposes, should be IsAuthenticated

    def get(self, request):
        latest = Telemetry.objects.select_related('drone').order_by('-timestamp')[:3]
        if latest.exists():
            data = []
            for t in latest:
                data.append({
                    'drone_id': t.drone.id,
                    'serial_number': t.drone.serial_number,
                    'latitude': t.latitude,
                    'longitude': t.longitude,
                    'altitude': t.altitude,
                    'battery_level': t.drone.battery_level,
                    'timestamp': t.timestamp.isoformat()
                })
            return Response(data)
        
        # Mock data if db is empty
        return Response([{
            'drone_id': 1,
            'latitude': 55.7558,
            'longitude': 37.6173,
            'altitude': 120.5,
            'speed': 12.4,
            'battery_level': 85,
            'timestamp': '2023-10-01T12:00:00Z'
        }])

class EmergencyStopView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, drone_id):
        try:
            drone = Drone.objects.get(id=drone_id)
        except Drone.DoesNotExist:
            return Response({'error': 'Drone not found'}, status=status.HTTP_404_NOT_FOUND)

        drone.status = 'maintenance'
        drone.save(update_fields=['status'])
        DeliveryMission.objects.filter(drone=drone, status='in_progress').update(status='emergency_stop')
        return Response({"status": "emergency_stop", "drone_id": drone_id})

class TelemetryViewSet(viewsets.ModelViewSet):
    queryset = Telemetry.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        client_type = self.request.headers.get('X-Client-Type', 'web')
        if client_type == 'mobile':
            return MobileTelemetrySerializer
        return WebTelemetrySerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        cache_key = f"latest_telemetry_drone_{instance.drone.id}"
        cache.set(cache_key, {
            'latitude': instance.latitude,
            'longitude': instance.longitude,
            'altitude': instance.altitude,
            'battery_level': instance.drone.battery_level
        }, timeout=300)
