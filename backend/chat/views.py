from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.permissions import RolePermission
from core.utils import serialize_doc
from chat.serializers import ChatHistorySerializer
from chat import services


class ChatHistoryView(APIView):
    allowed_roles = ["USER", "CAPTAIN", "RESTAURANT", "ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample: GET /api/v1/chat/history/<room_id>?limit=50
    def get(self, request, room_id: str):
        serializer = ChatHistorySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        if not services.is_participant(room_id, request.user.id, getattr(request.user, "role", None)):
            return Response({"detail": "Not allowed"}, status=403)
        limit = serializer.validated_data.get("limit", 50)
        messages = services.list_messages(room_id, limit=limit)
        return Response({"messages": serialize_doc(messages)})


class ChatMaskedCallView(APIView):
    allowed_roles = ["USER", "CAPTAIN", "RESTAURANT"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample: GET /api/v1/chat/call/<room_id>?callee_id=<id>
    def get(self, request, room_id: str):
        callee_id = request.query_params.get("callee_id")
        if not callee_id:
            return Response({"detail": "callee_id is required"}, status=400)
        if not services.is_participant(room_id, request.user.id, getattr(request.user, "role", None)):
            return Response({"detail": "Not allowed"}, status=403)
        data = services.get_masked_numbers(room_id, request.user.id, callee_id)
        return Response({"call": data})
