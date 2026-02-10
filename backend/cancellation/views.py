from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import RolePermission
from core.utils import serialize_doc
from cancellation.serializers import CancelOrderSerializer, CancelRideSerializer
from cancellation import services


class CancelPolicyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"policy": services.get_policy()})


class CancelOrderView(APIView):
    allowed_roles = ["USER", "CAPTAIN", "RESTAURANT", "ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"order_id": "<order_id>", "reason": "User cancelled", "late_delivery": false}
    def post(self, request):
        serializer = CancelOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        actor_role = serializer.validated_data.get("actor") or getattr(request.user, "role", None) or "SYSTEM"
        try:
            result = services.cancel_order(
                actor_id=request.user.id,
                order_id=serializer.validated_data["order_id"],
                actor_role=actor_role,
                reason=serializer.validated_data["reason"],
                late_delivery=serializer.validated_data.get("late_delivery", False),
                no_show=serializer.validated_data.get("no_show", False),
                metadata=serializer.validated_data.get("metadata"),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"result": serialize_doc(result)})


class CancelRideView(APIView):
    allowed_roles = ["USER", "CAPTAIN", "ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"ride_id": "<ride_id>", "reason": "User cancelled"}
    def post(self, request):
        serializer = CancelRideSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        actor_role = serializer.validated_data.get("actor") or getattr(request.user, "role", None) or "SYSTEM"
        try:
            result = services.cancel_ride(
                actor_id=request.user.id,
                ride_id=serializer.validated_data["ride_id"],
                actor_role=actor_role,
                reason=serializer.validated_data["reason"],
                no_show=serializer.validated_data.get("no_show", False),
                metadata=serializer.validated_data.get("metadata"),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"result": serialize_doc(result)})
