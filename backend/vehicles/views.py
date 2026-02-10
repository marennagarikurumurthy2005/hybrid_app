from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import RolePermission
from core.utils import serialize_doc
from vehicles.serializers import VehicleRegisterSerializer, VehicleRulesSerializer
from vehicles import services
from captains import services as captain_services


class VehicleRegisterView(APIView):
    allowed_roles = ["CAPTAIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"vehicle_type": "BIKE_EV", "vehicle_number": "KA01AB1234", "vehicle_brand": "Ather", "license_number": "DL123", "rc_image": "...", "license_image": "..."}
    def post(self, request):
        serializer = VehicleRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = captain_services.register_vehicle(request.user.id, serializer.validated_data)
        services.register_vehicle(request.user.id, serializer.validated_data)
        if not updated:
            return Response({"detail": "Captain not found"}, status=status.HTTP_404_NOT_FOUND)
        vehicle = captain_services.get_vehicle(request.user.id)
        return Response({"vehicle": serialize_doc(vehicle)})


class VehicleRulesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rules = services.get_rules()
        return Response({"rules": rules})

    def post(self, request):
        if getattr(request.user, "role", None) != "ADMIN":
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        serializer = VehicleRulesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rules = services.get_rules()
        rules.update(serializer.validated_data)
        updated = services.set_rules(rules)
        return Response({"rules": updated})
