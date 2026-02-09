from rest_framework import serializers


class WalletAnalyticsSerializer(serializers.Serializer):
    user_id = serializers.CharField()
