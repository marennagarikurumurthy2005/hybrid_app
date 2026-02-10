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


class RestaurantProfileUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    logo_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    opening_time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    closing_time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    is_open = serializers.BooleanField(required=False)
    support_phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
