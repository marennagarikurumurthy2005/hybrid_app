from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.permissions import RolePermission
from core.utils import serialize_doc
from rides.serializers import FareSerializer, CreateRideSerializer, VerifyRidePaymentSerializer, RideCompleteSerializer
from rides import services
from pricing import services as pricing_services


class RideFareView(APIView):
    allowed_roles = ["USER"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {
    #   "pickup_lat": 12.97,
    #   "pickup_lng": 77.59,
    #   "dropoff_lat": 12.93,
    #   "dropoff_lng": 77.61,
    #   "vehicle_type": "CAR"
    # }
    def post(self, request):
        serializer = FareSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_base_fare = services.calculate_fare(
            {"lat": serializer.validated_data["pickup_lat"], "lng": serializer.validated_data["pickup_lng"]},
            {"lat": serializer.validated_data["dropoff_lat"], "lng": serializer.validated_data["dropoff_lng"]},
            serializer.validated_data["vehicle_type"],
        )
        surge_multiplier = 1.0
        base_fare = int(round(raw_base_fare))
        total_fare = base_fare
        surge_amount = 0
        reward_preview = 0
        try:
            surge_data = pricing_services.calculate_surge(
                "RIDE",
                serializer.validated_data["pickup_lat"],
                serializer.validated_data["pickup_lng"],
                store_history=False,
            )
            surge_multiplier = float(surge_data.get("surge_multiplier", 1.0))
            total_fare = int(round(raw_base_fare * surge_multiplier))
            surge_amount = max(0, total_fare - base_fare)
        except Exception:
            pass
        from core.vehicles import is_ev_vehicle
        from vehicles import services as vehicle_services
        if is_ev_vehicle(serializer.validated_data["vehicle_type"]):
            reward_multiplier = vehicle_services.get_ev_reward_percentage() * vehicle_services.get_ev_bonus_multiplier()
            reward_preview = int(total_fare * reward_multiplier)
        return Response({
            "fare_base": base_fare,
            "surge_multiplier": round(surge_multiplier, 2),
            "surge_amount": surge_amount,
            "fare_total": total_fare,
            "reward_points_preview": reward_preview,
        })


class RideCreateView(APIView):
    allowed_roles = ["USER"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {
    #   "pickup_lat": 12.97,
    #   "pickup_lng": 77.59,
    #   "dropoff_lat": 12.93,
    #   "dropoff_lng": 77.61,
    #   "vehicle_type": "BIKE",
    #   "payment_mode": "WALLET + RAZORPAY",
    #   "wallet_amount": 2000,
    #   "redeem_points": 150
    # }
    def post(self, request):
        serializer = CreateRideSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            ride, razorpay_order = services.create_ride(
                user_id=request.user.id,
                pickup={"lat": serializer.validated_data["pickup_lat"], "lng": serializer.validated_data["pickup_lng"]},
                dropoff={"lat": serializer.validated_data["dropoff_lat"], "lng": serializer.validated_data["dropoff_lng"]},
                vehicle_type=serializer.validated_data["vehicle_type"],
                payment_mode=serializer.validated_data["payment_mode"],
                wallet_amount=serializer.validated_data.get("wallet_amount"),
                redeem_points=serializer.validated_data.get("redeem_points"),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"ride": serialize_doc(ride), "razorpay_order": razorpay_order}, status=status.HTTP_201_CREATED)


class RideVerifyPaymentView(APIView):
    allowed_roles = ["USER"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"ride_id": "<ride_id>", "razorpay_order_id": "order_abc", "razorpay_payment_id": "pay_123", "razorpay_signature": "sig"}
    def post(self, request):
        serializer = VerifyRidePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            ride = services.verify_ride_payment(
                serializer.validated_data["ride_id"],
                serializer.validated_data["razorpay_order_id"],
                serializer.validated_data["razorpay_payment_id"],
                serializer.validated_data["razorpay_signature"],
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"ride": serialize_doc(ride)})


class RideCompleteView(APIView):
    allowed_roles = ["CAPTAIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"ride_id": "<ride_id>"}
    def post(self, request):
        serializer = RideCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ride = services.complete_ride(serializer.validated_data["ride_id"])
        if not ride:
            return Response({"detail": "Ride not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"ride": serialize_doc(ride)})
