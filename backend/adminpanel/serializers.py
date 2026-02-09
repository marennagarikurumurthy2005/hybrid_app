from rest_framework import serializers


class AdminListSerializer(serializers.Serializer):
    limit = serializers.IntegerField(required=False, min_value=1, max_value=500)
    skip = serializers.IntegerField(required=False, min_value=0)
