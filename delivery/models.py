from django.db import models
from django.conf import settings

class Drone(models.Model):
    STATUS_CHOICES = [
        ('ready', 'Ready'),
        ('flying', 'Flying'),
        ('charging', 'Charging'),
        ('maintenance', 'Maintenance'),
    ]
    serial_number = models.CharField(max_length=100, unique=True)
    model_name = models.CharField(max_length=100)
    battery_level = models.IntegerField(default=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ready')

    def __str__(self):
        return f"{self.serial_number} - {self.model_name} ({self.status})"

class DeliveryMission(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('emergency_stop', 'Emergency Stop'),
    ]
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='delivery_missions')
    drone = models.ForeignKey(Drone, on_delete=models.SET_NULL, null=True, blank=True, related_name='missions')
    delivery_address = models.CharField(max_length=255, default='')
    order_content = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Mission {self.id} for {self.customer}"
