from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.permissions import RolePermission
from core.utils import serialize_doc
from orders.serializers import CheckoutSerializer, CreateOrderSerializer, VerifyPaymentSerializer
from orders import services
from pricing import services as pricing_services
from core.db import get_db
from core.utils import to_object_id


class OrderCheckoutView(APIView):
    allowed_roles = ["USER"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {
    #   "restaurant_id": "<restaurant_id>",
    #   "items": [{"menu_item_id": "<menu_id>", "quantity": 2}]
    # }
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            items, subtotal = services.calculate_food_totals(
                serializer.validated_data["restaurant_id"],
                serializer.validated_data["items"],
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        surge_multiplier = 1.0
        total_amount = subtotal
        surge_amount = 0
        try:
            db = get_db()
            restaurant = db.restaurants.find_one({"_id": to_object_id(serializer.validated_data["restaurant_id"])})
            pickup_location = restaurant.get("location") if restaurant else None
            if pickup_location and pickup_location.get("coordinates"):
                surge_data = pricing_services.calculate_surge(
                    "ORDER",
                    pickup_location["coordinates"][1],
                    pickup_location["coordinates"][0],
                    store_history=False,
                )
                surge_multiplier = float(surge_data.get("surge_multiplier", 1.0))
                total_amount = pricing_services.apply_surge(subtotal, surge_multiplier)
                surge_amount = max(0, total_amount - subtotal)
        except Exception:
            pass
        return Response({
            "items": serialize_doc(items),
            "subtotal": subtotal,
            "surge_multiplier": round(surge_multiplier, 2),
            "surge_amount": surge_amount,
            "total": total_amount,
        })


class OrderCreateView(APIView):
    allowed_roles = ["USER"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {
    #   "restaurant_id": "<restaurant_id>",
    #   "items": [{"menu_item_id": "<menu_id>", "quantity": 2}],
    #   "payment_mode": "WALLET + RAZORPAY",
    #   "wallet_amount": 5000
    # }
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order, items, razorpay_order = services.create_order(
                user_id=request.user.id,
                restaurant_id=serializer.validated_data["restaurant_id"],
                items=serializer.validated_data["items"],
                payment_mode=serializer.validated_data["payment_mode"],
                wallet_amount=serializer.validated_data.get("wallet_amount"),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "order": serialize_doc(order),
            "items": serialize_doc(items),
            "razorpay_order": razorpay_order,
        }, status=status.HTTP_201_CREATED)


class OrderVerifyPaymentView(APIView):
    allowed_roles = ["USER"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {
    #   "order_id": "<order_id>",
    #   "razorpay_order_id": "order_abc",
    #   "razorpay_payment_id": "pay_123",
    #   "razorpay_signature": "sig"
    # }
    def post(self, request):
        serializer = VerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = services.verify_order_payment(
                serializer.validated_data["order_id"],
                serializer.validated_data["razorpay_order_id"],
                serializer.validated_data["razorpay_payment_id"],
                serializer.validated_data["razorpay_signature"],
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"order": serialize_doc(order)})
