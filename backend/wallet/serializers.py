from rest_framework import serializers


class WalletRefundSerializer(serializers.Serializer):
    reference = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.IntegerField(min_value=1)
    reason = serializers.CharField()
    source = serializers.ChoiceField(choices=["FOOD", "RIDE", "REFUND"])


class WalletSettleSerializer(serializers.Serializer):
    limit = serializers.IntegerField(required=False, min_value=1, max_value=500)
