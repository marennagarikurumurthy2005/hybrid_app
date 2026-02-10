from rest_framework import serializers


class PayoutRequestSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1)


class BankLinkSerializer(serializers.Serializer):
    account_number = serializers.CharField()
    ifsc = serializers.CharField()
    name = serializers.CharField()
    upi = serializers.CharField(required=False, allow_blank=True)
