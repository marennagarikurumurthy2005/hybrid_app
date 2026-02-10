from rest_framework import serializers
from django.conf import settings


class FirebaseLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField()
    role = serializers.ChoiceField(choices=settings.ALLOWED_ROLES, required=False)
    device_id = serializers.CharField(required=False, allow_blank=True)
    device_name = serializers.CharField(required=False, allow_blank=True)


class FcmTokenSerializer(serializers.Serializer):
    fcm_token = serializers.CharField()


class UserProfileUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    avatar_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    default_address = serializers.JSONField(required=False, allow_null=True)
    preferences = serializers.JSONField(required=False, allow_null=True)


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=False, allow_blank=True)


class UserAddressCreateSerializer(serializers.Serializer):
    label = serializers.ChoiceField(choices=["HOME", "WORK", "OTHER"])
    line1 = serializers.CharField()
    line2 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    state = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    postal_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    landmark = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)
    is_default = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        lat = attrs.get("lat")
        lng = attrs.get("lng")
        if (lat is None) ^ (lng is None):
            raise serializers.ValidationError("lat and lng must be provided together")
        if lat is not None and (lat < -90 or lat > 90):
            raise serializers.ValidationError("Invalid latitude")
        if lng is not None and (lng < -180 or lng > 180):
            raise serializers.ValidationError("Invalid longitude")
        return attrs


class UserAddressUpdateSerializer(serializers.Serializer):
    label = serializers.ChoiceField(choices=["HOME", "WORK", "OTHER"], required=False)
    line1 = serializers.CharField(required=False, allow_blank=True)
    line2 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    state = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    postal_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    landmark = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)
    is_default = serializers.BooleanField(required=False)

    def validate(self, attrs):
        lat = attrs.get("lat")
        lng = attrs.get("lng")
        if (lat is None) ^ (lng is None):
            raise serializers.ValidationError("lat and lng must be provided together")
        if lat is not None and (lat < -90 or lat > 90):
            raise serializers.ValidationError("Invalid latitude")
        if lng is not None and (lng < -180 or lng > 180):
            raise serializers.ValidationError("Invalid longitude")
        return attrs


class FavoriteCreateSerializer(serializers.Serializer):
    favorite_type = serializers.ChoiceField(choices=["RESTAURANT", "MENU_ITEM"])
    reference_id = serializers.CharField()
