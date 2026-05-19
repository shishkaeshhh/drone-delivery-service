from rest_framework import serializers

from delivery.models import CatalogItem, DeliveryMission, Drone
from telemetry.models import Telemetry


class CatalogItemSerializer(serializers.ModelSerializer):
    store_display = serializers.CharField(source='get_store_display', read_only=True)

    class Meta:
        model = CatalogItem
        fields = ['id', 'store', 'store_display', 'name', 'price']


class DroneSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Drone
        fields = ['id', 'serial_number', 'model_name', 'battery_level', 'status']


class MissionSummarySerializer(serializers.ModelSerializer):
    drone = DroneSummarySerializer(read_only=True)
    customer_username = serializers.CharField(source='customer.username', read_only=True)

    class Meta:
        model = DeliveryMission
        fields = [
            'id',
            'customer_username',
            'drone',
            'delivery_address',
            'order_content',
            'status',
            'created_at',
            'updated_at',
        ]


class CustomerOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryMission
        fields = ['delivery_address', 'order_content']

    def validate_order_content(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError('order_content must be a non-empty list.')

        normalized_items = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                raise serializers.ValidationError(f'Item #{index} must be an object.')

            quantity = item.get('quantity', 1)
            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                raise serializers.ValidationError(f'Item #{index} quantity must be an integer.')
            if quantity <= 0:
                raise serializers.ValidationError(f'Item #{index} quantity must be greater than zero.')

            catalog_item = self._find_catalog_item(item)
            if catalog_item is None:
                raise serializers.ValidationError(
                    f'Item #{index} must reference an existing food item from the catalog.'
                )

            unit_price = float(catalog_item.price)
            normalized_items.append({
                'item_id': catalog_item.id,
                'store': catalog_item.store,
                'store_name': catalog_item.get_store_display(),
                'name': catalog_item.name,
                'quantity': quantity,
                'unit_price': unit_price,
                'line_total': round(unit_price * quantity, 2),
            })

        return normalized_items

    def _find_catalog_item(self, item):
        item_id = item.get('item_id') or item.get('id')
        if item_id:
            return CatalogItem.objects.filter(id=item_id).first()

        name = item.get('name')
        store = item.get('store')
        if not name:
            return None

        queryset = CatalogItem.objects.filter(name__iexact=name)
        if store:
            queryset = queryset.filter(store=store)
        return queryset.first()

    def create(self, validated_data):
        return DeliveryMission.objects.create(
            customer=self.context['request'].user,
            status='new',
            **validated_data,
        )


class TelemetrySnapshotSerializer(serializers.ModelSerializer):
    drone_id = serializers.IntegerField(source='drone.id', read_only=True)
    serial_number = serializers.CharField(source='drone.serial_number', read_only=True)
    battery_level = serializers.IntegerField(source='drone.battery_level', read_only=True)

    class Meta:
        model = Telemetry
        fields = [
            'id',
            'drone_id',
            'serial_number',
            'latitude',
            'longitude',
            'altitude',
            'battery_level',
            'timestamp',
        ]
