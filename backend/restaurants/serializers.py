from rest_framework import serializers


class RestaurantCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    address = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)


class MenuItemCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    price = serializers.IntegerField(min_value=1)
    is_available = serializers.BooleanField(required=False, default=True)
