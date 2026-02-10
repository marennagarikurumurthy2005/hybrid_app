from rest_framework import serializers


CANCEL_ACTORS = ["USER", "CAPTAIN", "RESTAURANT", "SYSTEM", "ADMIN"]


class CancelOrderSerializer(serializers.Serializer):
    order_id = serializers.CharField()
    actor = serializers.ChoiceField(choices=CANCEL_ACTORS, required=False)
    reason = serializers.CharField()
    late_delivery = serializers.BooleanField(required=False, default=False)
    no_show = serializers.BooleanField(required=False, default=False)
    metadata = serializers.DictField(required=False)


class CancelRideSerializer(serializers.Serializer):
    ride_id = serializers.CharField()
    actor = serializers.ChoiceField(choices=CANCEL_ACTORS, required=False)
    reason = serializers.CharField()
    no_show = serializers.BooleanField(required=False, default=False)
    metadata = serializers.DictField(required=False)
