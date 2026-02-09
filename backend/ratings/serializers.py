from rest_framework import serializers


class CaptainRateSerializer(serializers.Serializer):
    job_type = serializers.ChoiceField(choices=["ORDER", "RIDE"])
    job_id = serializers.CharField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True)


class CaptainStatsSerializer(serializers.Serializer):
    captain_id = serializers.CharField()
