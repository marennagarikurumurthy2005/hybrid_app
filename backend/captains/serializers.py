from rest_framework import serializers

from core.vehicles import normalize_vehicle_type, VEHICLE_TYPES


class OnlineStatusSerializer(serializers.Serializer):
    is_online = serializers.BooleanField()


class LocationSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()


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
