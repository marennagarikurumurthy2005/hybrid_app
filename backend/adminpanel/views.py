from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import RolePermission
from core.utils import serialize_doc
from adminpanel import services
from adminpanel.serializers import AdminCaptainVerifySerializer


class AdminOverviewView(APIView):
    allowed_roles = ["ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        data = services.overview()
        return Response({"overview": data})


class AdminUsersView(APIView):
    allowed_roles = ["ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        limit = int(request.query_params.get("limit", 50))
        skip = int(request.query_params.get("skip", 0))
        users = services.list_users(limit=limit, skip=skip)
        return Response({"users": serialize_doc(users)})


class AdminCaptainsView(APIView):
    allowed_roles = ["ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        limit = int(request.query_params.get("limit", 50))
        skip = int(request.query_params.get("skip", 0))
        captains = services.list_captains(limit=limit, skip=skip)
        return Response({"captains": serialize_doc(captains)})


class AdminCaptainVerifyView(APIView):
    allowed_roles = ["ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"is_verified": true, "reason": "Documents verified"}
    def post(self, request, captain_id: str):
        serializer = AdminCaptainVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = services.verify_captain(
            captain_id,
            serializer.validated_data["is_verified"],
            serializer.validated_data.get("reason"),
        )
        if not updated:
            return Response({"detail": "Captain not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"captain": serialize_doc(updated)})
