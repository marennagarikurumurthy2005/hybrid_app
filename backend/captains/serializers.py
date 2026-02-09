from rest_framework import serializers


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
