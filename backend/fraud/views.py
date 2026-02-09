from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import RolePermission
from core.utils import serialize_doc
from fraud import services


class FraudScanView(APIView):
    allowed_roles = ["ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        limit = int(request.query_params.get("limit", 200))
        suspicious = services.scan_users(limit=limit)
        return Response({"suspicious": serialize_doc(suspicious)})
