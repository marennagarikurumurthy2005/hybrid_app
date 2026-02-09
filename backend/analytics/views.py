from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import RolePermission
from analytics import services


class WalletAnalyticsView(APIView):
    allowed_roles = ["USER", "ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request, user_id: str):
        role = getattr(request, "role", None) or getattr(request.user, "role", None)
        if role == "USER" and request.user.id != user_id:
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        data = services.wallet_analytics(user_id)
        if not data:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"analytics": data})
