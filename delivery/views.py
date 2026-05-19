from rest_framework import viewsets, permissions
from .models import DeliveryMission, Drone
from .serializers import WebMissionSerializer, MobileMissionSerializer, DroneSerializer
from rest_framework.response import Response
from rest_framework.decorators import action

class DroneViewSet(viewsets.ModelViewSet):
    queryset = Drone.objects.all()
    serializer_class = DroneSerializer
    permission_classes = [permissions.IsAuthenticated]

class MissionViewSet(viewsets.ModelViewSet):
    queryset = DeliveryMission.objects.all()
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
            drone.status = 'flying'
            drone.save()

    @action(detail=True, methods=['post'])
    def start_mission(self, request, pk=None):
        mission = self.get_object()
        drone_id = request.data.get('drone_id') or request.POST.get('drone_id')

        if mission.status == 'new' and drone_id:
            try:
                drone = Drone.objects.get(id=drone_id, status='ready')
                mission.drone = drone
                mission.status = 'in_progress'
                mission.save()

                drone.status = 'flying'
                drone.save()
                return Response({'status': 'Mission started', 'drone_assigned': drone.serial_number})
            except Drone.DoesNotExist:
                return Response({'error': 'Drone not available'}, status=400)
        return Response({'error': 'Mission cannot be started or invalid drone'}, status=400)

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

from rest_framework.views import APIView
from .models import CatalogItem

class CatalogSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        store = request.GET.get('store', '')
        q = request.GET.get('q', '')

        items = CatalogItem.objects.all()
        if store:
            items = items.filter(store=store)
        if q:
            items = items.filter(name__icontains=q)

        data = [{'id': item.id, 'name': item.name, 'price': str(item.price)} for item in items[:20]]
        return Response(data)

class CatalogPriceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        item_id = request.GET.get('item_id')
        try:
            item = CatalogItem.objects.get(id=item_id)
            return Response({'id': item.id, 'price': str(item.price)})
        except CatalogItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=404)
