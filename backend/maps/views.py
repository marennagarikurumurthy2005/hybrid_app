from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import RolePermission
from core.utils import serialize_doc
from maps.serializers import RouteRequestSerializer, EtaRequestSerializer, NearbyCaptainsSerializer
from maps import services


class MapsRouteView(APIView):
    allowed_roles = ["USER", "CAPTAIN", "RESTAURANT", "ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"origin_lat": 12.97, "origin_lng": 77.59, "destination_lat": 12.93, "destination_lng": 77.61}
    def post(self, request):
        serializer = RouteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = services.get_route(
                {"lat": serializer.validated_data["origin_lat"], "lng": serializer.validated_data["origin_lng"]},
                {"lat": serializer.validated_data["destination_lat"], "lng": serializer.validated_data["destination_lng"]},
                serializer.validated_data.get("mode", "driving"),
            )
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"route": serialize_doc(result)})


class MapsEtaView(APIView):
    allowed_roles = ["USER", "CAPTAIN", "RESTAURANT", "ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"origin_lat": 12.97, "origin_lng": 77.59, "destination_lat": 12.93, "destination_lng": 77.61}
    def post(self, request):
        serializer = EtaRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = services.get_eta(
                {"lat": serializer.validated_data["origin_lat"], "lng": serializer.validated_data["origin_lng"]},
                {"lat": serializer.validated_data["destination_lat"], "lng": serializer.validated_data["destination_lng"]},
                serializer.validated_data.get("mode", "driving"),
            )
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"eta": result})


class NearbyCaptainsView(APIView):
    allowed_roles = ["USER", "ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Example query:
    # /api/captain/nearby?lat=12.97&lng=77.59&radius_m=3000
    def get(self, request):
        serializer = NearbyCaptainsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        captains = services.find_nearby_captains(
            serializer.validated_data["lat"],
            serializer.validated_data["lng"],
            serializer.validated_data.get("radius_m", 5000),
        )
        return Response({"captains": serialize_doc(captains)})
