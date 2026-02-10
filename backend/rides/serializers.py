from rest_framework import serializers

from core.vehicles import normalize_vehicle_type, VEHICLE_TYPES


class FareSerializer(serializers.Serializer):
    pickup_lat = serializers.FloatField()
    pickup_lng = serializers.FloatField()
    dropoff_lat = serializers.FloatField()
    dropoff_lng = serializers.FloatField()
    vehicle_type = serializers.CharField()

    def validate_vehicle_type(self, value):
        normalized = normalize_vehicle_type(value)
        if not normalized:
            raise serializers.ValidationError(f"Invalid vehicle_type. Allowed: {', '.join(VEHICLE_TYPES)}")
        return normalized


class CreateRideSerializer(serializers.Serializer):
    pickup_lat = serializers.FloatField()
    pickup_lng = serializers.FloatField()
    dropoff_lat = serializers.FloatField()
    dropoff_lng = serializers.FloatField()
    vehicle_type = serializers.CharField()
    payment_mode = serializers.CharField()
    wallet_amount = serializers.IntegerField(required=False, min_value=0)

    def validate_vehicle_type(self, value):
        normalized = normalize_vehicle_type(value)
        if not normalized:
            raise serializers.ValidationError(f"Invalid vehicle_type. Allowed: {', '.join(VEHICLE_TYPES)}")
        return normalized


class VerifyRidePaymentSerializer(serializers.Serializer):
    ride_id = serializers.CharField()
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()


class RideCompleteSerializer(serializers.Serializer):
    ride_id = serializers.CharField()
