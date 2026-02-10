from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import RolePermission
from core.utils import serialize_doc
from promotions.serializers import CouponApplySerializer, ReferralUseSerializer
from promotions import services


class CouponApplyView(APIView):
    allowed_roles = ["USER"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"code": "WELCOME", "amount": 25000, "job_type": "ORDER"}
    def post(self, request):
        serializer = CouponApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = services.apply_coupon(
                request.user.id,
                serializer.validated_data["code"],
                serializer.validated_data["amount"],
                serializer.validated_data["job_type"],
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"coupon": result})


class ReferralUseView(APIView):
    allowed_roles = ["USER"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"referral_code": "GORIDES123"}
    def post(self, request):
        serializer = ReferralUseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            services.use_referral(request.user.id, serializer.validated_data["referral_code"])
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"used": True})


class ActiveCampaignsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get("limit", 50))
        campaigns = services.list_active_campaigns(limit=limit)
        return Response({"campaigns": serialize_doc(campaigns)})
