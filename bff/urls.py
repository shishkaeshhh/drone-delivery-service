from django.urls import path

from .views import (
    CustomerDashboardBFFView,
    HealthCheckView,
    ManagerDashboardBFFView,
    OperatorControlBFFView,
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='bff-health'),
    path('customer/dashboard/', CustomerDashboardBFFView.as_view(), name='bff-customer-dashboard'),
    path('manager/dashboard/', ManagerDashboardBFFView.as_view(), name='bff-manager-dashboard'),
    path('operator/control/', OperatorControlBFFView.as_view(), name='bff-operator-control'),
]
