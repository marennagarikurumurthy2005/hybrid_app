from rest_framework import serializers


class DeviceRegisterSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    platform = serializers.CharField(required=False, allow_blank=True)
    fingerprint = serializers.CharField(required=False, allow_blank=True)
    ip = serializers.CharField(required=False, allow_blank=True)
    meta = serializers.DictField(required=False)


class TrustScanSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=False, allow_blank=True)


class RiskScoreSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    device_id = serializers.CharField(required=False, allow_blank=True)
