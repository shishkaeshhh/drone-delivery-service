from rest_framework import serializers
from .models import Telemetry

class WebTelemetrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Telemetry
        fields = '__all__'

class MobileTelemetrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Telemetry
        fields = ['latitude', 'longitude', 'altitude', 'battery_level']
