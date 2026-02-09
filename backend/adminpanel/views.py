from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.permissions import RolePermission
from core.utils import serialize_doc
from adminpanel import services


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
