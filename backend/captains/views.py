from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.permissions import RolePermission
from core.utils import serialize_doc
from captains.serializers import (
    OnlineStatusSerializer,
    LocationSerializer,
    JobSerializer,
    JobCreateSerializer,
    JobDecisionSerializer,
    VehicleRegisterSerializer,
    GoHomeEnableSerializer,
)
from captains import services
from core import matching_service


class CaptainOnlineView(APIView):
    allowed_roles = ["CAPTAIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"is_online": true}
    def post(self, request):
        serializer = OnlineStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            updated = services.set_online_status(request.user.id, serializer.validated_data["is_online"])
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return Response({"captain": serialize_doc(updated)})


class CaptainLocationView(APIView):
    allowed_roles = ["CAPTAIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"lat": 12.9716, "lng": 77.5946}
    def post(self, request):
        serializer = LocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = services.update_location(
            request.user.id,
            serializer.validated_data["lat"],
            serializer.validated_data["lng"],
        )
        return Response({"captain": serialize_doc(updated)})


class CaptainAcceptJobView(APIView):
    allowed_roles = ["CAPTAIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"job_type": "ORDER", "job_id": "<order_id>"}
    def post(self, request):
        serializer = JobSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            job = matching_service.accept_job(
                serializer.validated_data["job_type"],
                serializer.validated_data["job_id"],
                request.user.id,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"job": serialize_doc(job)})


class CaptainCompleteJobView(APIView):
    allowed_roles = ["CAPTAIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"job_type": "ORDER", "job_id": "<order_id>"}
    def post(self, request):
        serializer = JobSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            job = matching_service.complete_job(
                serializer.validated_data["job_type"],
                serializer.validated_data["job_id"],
                request.user.id,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"job": serialize_doc(job)})


class JobCreateView(APIView):
    allowed_roles = ["USER", "RESTAURANT"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"job_type": "ORDER", "job_id": "<order_id>"}
    def post(self, request):
        serializer = JobCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            candidates = matching_service.create_job(
                serializer.validated_data["job_type"],
                serializer.validated_data["job_id"],
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"candidates": candidates}, status=status.HTTP_201_CREATED)


class JobAcceptView(APIView):
    allowed_roles = ["CAPTAIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"job_type": "ORDER", "job_id": "<order_id>"}
    def post(self, request):
        serializer = JobDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            job = matching_service.accept_job(
                serializer.validated_data["job_type"],
                serializer.validated_data["job_id"],
                request.user.id,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"job": serialize_doc(job)})


class JobRejectView(APIView):
    allowed_roles = ["CAPTAIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"job_type": "ORDER", "job_id": "<order_id>"}
    def post(self, request):
        serializer = JobDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            matching_service.reject_job(
                serializer.validated_data["job_type"],
                serializer.validated_data["job_id"],
                request.user.id,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"rejected": True})


class JobCompleteView(APIView):
    allowed_roles = ["CAPTAIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"job_type": "ORDER", "job_id": "<order_id>"}
    def post(self, request):
        serializer = JobDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            job = matching_service.complete_job(
                serializer.validated_data["job_type"],
                serializer.validated_data["job_id"],
                request.user.id,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"job": serialize_doc(job)})


class CaptainVehicleRegisterView(APIView):
    allowed_roles = ["CAPTAIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {
    #   "vehicle_type": "BIKE",
    #   "vehicle_number": "KA01AB1234",
    #   "vehicle_brand": "Honda",
    #   "license_number": "DL123456789",
    #   "rc_image": "https://cdn.example.com/rc.jpg",
    #   "license_image": "https://cdn.example.com/license.jpg"
    # }
    def post(self, request):
        serializer = VehicleRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = services.register_vehicle(request.user.id, serializer.validated_data)
        if not updated:
            return Response({"detail": "Captain not found"}, status=status.HTTP_404_NOT_FOUND)
        vehicle = services.get_vehicle(request.user.id)
        return Response({"vehicle": serialize_doc(vehicle), "captain": serialize_doc(updated)})


class CaptainVehicleMeView(APIView):
    allowed_roles = ["CAPTAIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        vehicle = services.get_vehicle(request.user.id)
        if not vehicle:
            return Response({"detail": "Captain not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"vehicle": serialize_doc(vehicle)})


class CaptainGoHomeEnableView(APIView):
    allowed_roles = ["CAPTAIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"lat": 17.385044, "lng": 78.486671}
    def post(self, request):
        serializer = GoHomeEnableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = services.enable_go_home(
            request.user.id,
            serializer.validated_data["lat"],
            serializer.validated_data["lng"],
        )
        if not updated:
            return Response({"detail": "Captain not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"captain": serialize_doc(updated)})


class CaptainGoHomeDisableView(APIView):
    allowed_roles = ["CAPTAIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    def post(self, request):
        updated = services.disable_go_home(request.user.id)
        if not updated:
            return Response({"detail": "Captain not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"captain": serialize_doc(updated)})
