from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import RolePermission
from routing.serializers import RouteOptimizeSerializer
from routing import services


class RouteOptimizeView(APIView):
    allowed_roles = ["USER", "CAPTAIN", "RESTAURANT", "ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"points": [{"lat": 12.97, "lng": 77.59}, {"lat": 12.95, "lng": 77.6}], "clusters": 2}
    def post(self, request):
        serializer = RouteOptimizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        points = serializer.validated_data["points"]
        optimized = services.optimize_route(points, serializer.validated_data.get("clusters"))
        return Response({"optimized": optimized}, status=status.HTTP_200_OK)
