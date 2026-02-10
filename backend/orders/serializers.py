from rest_framework import serializers


class CheckoutItemSerializer(serializers.Serializer):
    menu_item_id = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1)


class CheckoutSerializer(serializers.Serializer):
    restaurant_id = serializers.CharField()
    items = CheckoutItemSerializer(many=True)
    redeem_points = serializers.IntegerField(required=False, min_value=0)


class CreateOrderSerializer(serializers.Serializer):
    restaurant_id = serializers.CharField()
    items = CheckoutItemSerializer(many=True)
    payment_mode = serializers.CharField()
    wallet_amount = serializers.IntegerField(required=False, min_value=0)
    redeem_points = serializers.IntegerField(required=False, min_value=0)


class VerifyPaymentSerializer(serializers.Serializer):
    order_id = serializers.CharField()
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()


class ReorderSerializer(serializers.Serializer):
    payment_mode = serializers.CharField()
    wallet_amount = serializers.IntegerField(required=False, min_value=0)
    redeem_points = serializers.IntegerField(required=False, min_value=0)
