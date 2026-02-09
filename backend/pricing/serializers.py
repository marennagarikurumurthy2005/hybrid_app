from rest_framework import serializers


class PricingCalculateSerializer(serializers.Serializer):
    job_type = serializers.ChoiceField(choices=["ORDER", "RIDE"])
    lat = serializers.FloatField()
    lng = serializers.FloatField()
