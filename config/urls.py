from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from telemetry.views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/delivery/', include('delivery.urls')),
    path('api/telemetry/', include('telemetry.urls')),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
