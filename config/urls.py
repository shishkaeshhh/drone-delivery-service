from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from delivery.views import CatalogSearchView, CatalogPriceView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/bff/', include('bff.urls')),
    path('api/delivery/', include('delivery.urls')),
    path('api/telemetry/', include('telemetry.urls')),
    path('api/catalog/search/', CatalogSearchView.as_view(), name='catalog-search'),
    path('api/catalog/price/', CatalogPriceView.as_view(), name='catalog-price'),
]
