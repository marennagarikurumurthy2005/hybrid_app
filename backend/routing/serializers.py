from rest_framework import serializers


class RouteOptimizeSerializer(serializers.Serializer):
    points = serializers.ListField(child=serializers.DictField(), allow_empty=False)
    clusters = serializers.IntegerField(required=False, min_value=1, max_value=10)
