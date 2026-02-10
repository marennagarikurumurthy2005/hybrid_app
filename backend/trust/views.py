from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import RolePermission
from core.utils import serialize_doc
from trust.serializers import DeviceRegisterSerializer
from trust import services


class DeviceRegisterView(APIView):
    allowed_roles = ["USER", "CAPTAIN", "RESTAURANT", "ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"device_id": "device-123", "platform": "android", "fingerprint": "hash"}
    def post(self, request):
        serializer = DeviceRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device = services.register_device(
            request.user.id,
            serializer.validated_data["device_id"],
            serializer.validated_data.get("platform"),
            serializer.validated_data.get("fingerprint"),
            serializer.validated_data.get("ip"),
            serializer.validated_data.get("meta"),
        )
        return Response({"device": serialize_doc(device)})


class TrustScanView(APIView):
    allowed_roles = ["ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        user_id = request.query_params.get("user_id")
        result = services.scan_user(user_id)
        return Response(result)
