from rest_framework import serializers

from core.vehicles import normalize_vehicle_type, VEHICLE_TYPES


class OnlineStatusSerializer(serializers.Serializer):
    is_online = serializers.BooleanField()


class LocationSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()


class GoHomeEnableSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()

    def validate_lat(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError("Invalid latitude")
        return value

    def validate_lng(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError("Invalid longitude")
        return value


class HomeLocationSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()

    def validate_lat(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError("Invalid latitude")
        return value

    def validate_lng(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError("Invalid longitude")
        return value


class JobSerializer(serializers.Serializer):
    job_type = serializers.ChoiceField(choices=["ORDER", "RIDE"])
    job_id = serializers.CharField()


class JobCreateSerializer(serializers.Serializer):
    job_type = serializers.ChoiceField(choices=["ORDER", "RIDE"])
    job_id = serializers.CharField()


class JobDecisionSerializer(serializers.Serializer):
    job_type = serializers.ChoiceField(choices=["ORDER", "RIDE"])
    job_id = serializers.CharField()


class VehicleRegisterSerializer(serializers.Serializer):
    vehicle_type = serializers.CharField()
    vehicle_number = serializers.CharField()
    vehicle_brand = serializers.CharField()
    license_number = serializers.CharField()
    rc_image = serializers.CharField()
    license_image = serializers.CharField()

    def validate_vehicle_type(self, value):
        normalized = normalize_vehicle_type(value)
        if not normalized:
            raise serializers.ValidationError(f"Invalid vehicle_type. Allowed: {', '.join(VEHICLE_TYPES)}")
        return normalized


class CaptainProfileUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    avatar_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    vehicle_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    vehicle_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    home_location = HomeLocationSerializer(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_vehicle_type(self, value):
        if value in (None, ""):
            return value
        normalized = normalize_vehicle_type(value)
        if not normalized:
            raise serializers.ValidationError(f"Invalid vehicle_type. Allowed: {', '.join(VEHICLE_TYPES)}")
        return normalized
