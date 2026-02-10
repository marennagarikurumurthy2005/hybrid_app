from rest_framework import serializers


class ExperimentAssignSerializer(serializers.Serializer):
    experiment_key = serializers.CharField()
    variants = serializers.ListField(child=serializers.CharField(), min_length=1)
