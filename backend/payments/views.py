from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from payments.serializers import RazorpayCreateOrderSerializer, RazorpayVerifySerializer
from payments import services


class RazorpayCreateOrderView(APIView):
    # Sample payload:
    # {"amount": 15000, "currency": "INR", "receipt": "order_123"}
    def post(self, request):
        serializer = RazorpayCreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = services.create_razorpay_order(
                amount=serializer.validated_data["amount"],
                currency=serializer.validated_data.get("currency", "INR"),
                receipt=serializer.validated_data["receipt"],
            )
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"razorpay_order": order}, status=status.HTTP_201_CREATED)


class RazorpayVerifyView(APIView):
    # Sample payload:
    # {"razorpay_order_id": "order_abc", "razorpay_payment_id": "pay_123", "razorpay_signature": "sig"}
    def post(self, request):
        serializer = RazorpayVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            services.verify_razorpay_signature(
                serializer.validated_data["razorpay_order_id"],
                serializer.validated_data["razorpay_payment_id"],
                serializer.validated_data["razorpay_signature"],
            )
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"verified": True})
