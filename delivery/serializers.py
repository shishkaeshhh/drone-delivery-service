from rest_framework import serializers
from .models import DeliveryMission, Drone

class DroneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drone
        fields = '__all__'

class WebMissionSerializer(serializers.ModelSerializer):
    drone_details = DroneSerializer(source='drone', read_only=True)
    customer = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = DeliveryMission
        fields = ['id', 'customer', 'drone', 'drone_details', 'delivery_address', 'order_content', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']

class MobileMissionSerializer(serializers.ModelSerializer):
    current_coordinates = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryMission
        fields = ['id', 'status', 'current_coordinates']

    def get_current_coordinates(self, obj):
        if obj.drone and obj.drone.telemetry_logs.exists():
            latest = obj.drone.telemetry_logs.latest('timestamp')
            return {'latitude': latest.latitude, 'longitude': latest.longitude}
        return None
