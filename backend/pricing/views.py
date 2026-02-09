from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import RolePermission
from pricing.serializers import PricingCalculateSerializer
from pricing import services


class PricingCalculateView(APIView):
    allowed_roles = ["USER", "CAPTAIN", "RESTAURANT", "ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"job_type": "RIDE", "lat": 12.97, "lng": 77.59}
    def post(self, request):
        serializer = PricingCalculateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = services.calculate_surge(
            serializer.validated_data["job_type"],
            serializer.validated_data["lat"],
            serializer.validated_data["lng"],
        )
        return Response({"surge": data}, status=status.HTTP_200_OK)
