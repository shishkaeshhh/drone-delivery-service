from rest_framework import viewsets, permissions
from .models import Mission, Drone
from .serializers import WebMissionSerializer, MobileMissionSerializer, DroneSerializer
from rest_framework.response import Response
from rest_framework.decorators import action

class DroneViewSet(viewsets.ModelViewSet):
    queryset = Drone.objects.all()
    serializer_class = DroneSerializer
    permission_classes = [permissions.IsAuthenticated]

class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        client_type = self.request.headers.get('X-Client-Type', 'web')
        if client_type == 'mobile':
            return MobileMissionSerializer
        return WebMissionSerializer

    def perform_create(self, serializer):
        drone = Drone.objects.filter(status='ready').first()
        serializer.save(customer=self.request.user, drone=drone)
        if drone:
            drone.status = 'in_flight'
            drone.save()

    @action(detail=True, methods=['post'])
    def start_mission(self, request, pk=None):
        mission = self.get_object()
        if mission.status == 'pending':
            mission.status = 'in_progress'
            mission.save()
            return Response({'status': 'Mission started'})
        return Response({'error': 'Mission cannot be started'}, status=400)

    @action(detail=True, methods=['post'])
    def complete_mission(self, request, pk=None):
        mission = self.get_object()
        if mission.status == 'in_progress':
            mission.status = 'completed'
            mission.save()
            if mission.drone:
                mission.drone.status = 'ready'
                mission.drone.save()
            return Response({'status': 'Mission completed'})
        return Response({'error': 'Mission not in progress'}, status=400)
