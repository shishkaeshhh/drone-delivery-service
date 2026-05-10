from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.generic import TemplateView
from django.core.cache import cache
from .models import Telemetry
from .serializers import WebTelemetrySerializer, MobileTelemetrySerializer

class DashboardView(TemplateView):
    template_name = 'telemetry/dashboard.html'

class LatestTelemetryView(APIView):
    permission_classes = [permissions.AllowAny] # For demo purposes, should be IsAuthenticated

    def get(self, request):
        # In a real scenario, this would group by drone/mission
        # Here we just return mock data or the latest entries
        latest = Telemetry.objects.order_by('-timestamp')[:3]
        if latest.exists():
            data = []
            for t in latest:
                data.append({
                    'drone_id': t.mission.drone.id if t.mission and hasattr(t.mission, 'drone') else t.id,
                    'latitude': t.latitude,
                    'longitude': t.longitude,
                    'altitude': t.altitude,
                    'speed': 15.5, # mock speed
                    'battery_level': t.battery_level,
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
    permission_classes = [permissions.AllowAny]

    def patch(self, request, drone_id):
        # Logic to handle emergency stop
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
        # Cache latest telemetry for quick access
        cache_key = f"latest_telemetry_{instance.mission.id}"
        cache.set(cache_key, {
            'latitude': instance.latitude,
            'longitude': instance.longitude,
            'altitude': instance.altitude,
            'battery_level': instance.battery_level
        }, timeout=300)
