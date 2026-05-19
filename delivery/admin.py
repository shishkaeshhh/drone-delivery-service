from django.contrib import admin
from django.utils.html import format_html
from .models import Drone, DeliveryMission, CatalogItem

@admin.register(CatalogItem)
class CatalogItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'price')
    list_filter = ('store',)
    search_fields = ('name',)

@admin.register(Drone)
class DroneAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'model_name', 'battery_level', 'status_colored')
    list_filter = ('status',)
    search_fields = ('serial_number', 'model_name')

    def status_colored(self, obj):
        colors = {
            'ready': 'green',
            'flying': 'blue',
            'charging': 'orange',
            'maintenance': 'red'
        }
        color = colors.get(obj.status, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_status_display())
    status_colored.short_description = 'Status'

@admin.register(DeliveryMission)
class DeliveryMissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'drone', 'delivery_address', 'status', 'created_at')
    list_filter = ('status', 'customer', 'delivery_address')
    search_fields = ('delivery_address', 'customer__username')
