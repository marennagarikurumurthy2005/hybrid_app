from rest_framework import serializers


class EtaPredictSerializer(serializers.Serializer):
    origin_lat = serializers.FloatField()
    origin_lng = serializers.FloatField()
    destination_lat = serializers.FloatField()
    destination_lng = serializers.FloatField()
    prep_time_min = serializers.IntegerField(required=False, min_value=0, default=0)
    batch_size = serializers.IntegerField(required=False, min_value=1, default=1)
    traffic_factor = serializers.FloatField(required=False, min_value=0.5, default=1.0)
    weather_factor = serializers.FloatField(required=False, min_value=0.5, default=1.0)
