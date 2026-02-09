from rest_framework import serializers


class FareSerializer(serializers.Serializer):
    pickup_lat = serializers.FloatField()
    pickup_lng = serializers.FloatField()
    dropoff_lat = serializers.FloatField()
    dropoff_lng = serializers.FloatField()


class CreateRideSerializer(serializers.Serializer):
    pickup_lat = serializers.FloatField()
    pickup_lng = serializers.FloatField()
    dropoff_lat = serializers.FloatField()
    dropoff_lng = serializers.FloatField()
    payment_mode = serializers.CharField()
    wallet_amount = serializers.IntegerField(required=False, min_value=0)


class VerifyRidePaymentSerializer(serializers.Serializer):
    ride_id = serializers.CharField()
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()


class RideCompleteSerializer(serializers.Serializer):
    ride_id = serializers.CharField()
