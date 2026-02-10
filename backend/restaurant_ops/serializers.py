from rest_framework import serializers


class RestaurantOrderUpdateSerializer(serializers.Serializer):
    order_id = serializers.CharField()
    status = serializers.CharField()
    prep_time_min = serializers.IntegerField(required=False, min_value=0)


class RestaurantItemToggleSerializer(serializers.Serializer):
    menu_item_id = serializers.CharField()
    is_available = serializers.BooleanField()
