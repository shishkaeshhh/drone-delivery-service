from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MissionViewSet, DroneViewSet

router = DefaultRouter()
router.register(r'missions', MissionViewSet)
router.register(r'drones', DroneViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
