from rest_framework import serializers


class RouteRequestSerializer(serializers.Serializer):
    origin_lat = serializers.FloatField()
    origin_lng = serializers.FloatField()
    destination_lat = serializers.FloatField()
    destination_lng = serializers.FloatField()
    mode = serializers.CharField(required=False, default="driving")


class EtaRequestSerializer(serializers.Serializer):
    origin_lat = serializers.FloatField()
    origin_lng = serializers.FloatField()
    destination_lat = serializers.FloatField()
    destination_lng = serializers.FloatField()
    mode = serializers.CharField(required=False, default="driving")


class NearbyCaptainsSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    radius_m = serializers.IntegerField(required=False, min_value=100, max_value=20000)
