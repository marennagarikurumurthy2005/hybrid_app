from rest_framework import serializers


class AdminCaptainVerifySerializer(serializers.Serializer):
    is_verified = serializers.BooleanField()
    reason = serializers.CharField(required=False, allow_blank=True)
