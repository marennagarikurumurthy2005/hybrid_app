from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import RolePermission
from core.utils import serialize_doc
from support.serializers import SupportTicketSerializer
from support import services


class SupportTicketCreateView(APIView):
    allowed_roles = ["USER", "CAPTAIN", "RESTAURANT"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"subject": "Refund issue", "message": "I was charged twice", "priority": "HIGH"}
    def post(self, request):
        serializer = SupportTicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = services.create_ticket(
            request.user.id,
            getattr(request.user, "role", None),
            serializer.validated_data["subject"],
            serializer.validated_data["message"],
            category=serializer.validated_data.get("category"),
            priority=serializer.validated_data.get("priority"),
        )
        return Response({"ticket": serialize_doc(ticket)}, status=status.HTTP_201_CREATED)
