from rest_framework import serializers

from core.vehicles import VEHICLE_TYPES


class VehicleRegisterSerializer(serializers.Serializer):
    vehicle_type = serializers.ChoiceField(choices=VEHICLE_TYPES)
    vehicle_number = serializers.CharField()
    vehicle_brand = serializers.CharField()
    license_number = serializers.CharField()
    rc_image = serializers.CharField()
    license_image = serializers.CharField()


class VehicleRulesSerializer(serializers.Serializer):
    food_allowed_vehicles = serializers.ListField(child=serializers.CharField(), required=False)
    ev_reward_percentage = serializers.FloatField(required=False)
    ev_bonus_multiplier = serializers.FloatField(required=False)
