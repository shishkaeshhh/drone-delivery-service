from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TelemetryViewSet, LatestTelemetryView, EmergencyStopView

router = DefaultRouter()
router.register(r'logs', TelemetryViewSet, basename='telemetry')

urlpatterns = [
    path('latest/', LatestTelemetryView.as_view(), name='telemetry-latest'),
    path('drones/<int:drone_id>/stop/', EmergencyStopView.as_view(), name='telemetry-stop'),
    path('', include(router.urls)),
]
