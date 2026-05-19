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

class CatalogItem(models.Model):
    STORE_CHOICES = [
        ('vkusvill', 'ВкусВилл'),
        ('magnit', 'Магнит'),
        ('pyaterochka', 'Пятерочка'),
        ('lenta', 'Лента'),
        ('depo', 'Фудмолл Депо'),
        ('syrovarnya', 'Сыроварня'),
        ('white_rabbit', 'White Rabbit'),
        ('pushkin', 'Кафе Пушкинъ')
    ]
    store = models.CharField(max_length=50, choices=STORE_CHOICES)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.get_store_display()}) - {self.price} руб."
