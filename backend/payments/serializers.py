from rest_framework import serializers


class RazorpayCreateOrderSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1)
    currency = serializers.CharField(required=False, default="INR")
    receipt = serializers.CharField()


class RazorpayVerifySerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()
