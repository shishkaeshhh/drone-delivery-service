from django.db import models
from delivery.models import Drone

class Telemetry(models.Model):
    drone = models.ForeignKey(Drone, on_delete=models.CASCADE, related_name='telemetry_logs')
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Telemetry for Drone {self.drone.serial_number} at {self.timestamp}"
