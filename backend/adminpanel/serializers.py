from rest_framework import serializers


class AdminCaptainVerifySerializer(serializers.Serializer):
    is_verified = serializers.BooleanField()
    reason = serializers.CharField(required=False, allow_blank=True)


class AdminRecommendRestaurantSerializer(serializers.Serializer):
    restaurant_id = serializers.CharField()
    is_recommended = serializers.BooleanField(required=False, default=True)


class AdminRecommendMenuSerializer(serializers.Serializer):
    menu_item_id = serializers.CharField()
    is_recommended = serializers.BooleanField(required=False, default=True)
