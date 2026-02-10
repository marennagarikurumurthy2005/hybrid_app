from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import RolePermission
from core.utils import serialize_doc
from notifications.serializers import SendNotificationSerializer, ScheduleNotificationSerializer
from notifications import services


class SendNotificationView(APIView):
    allowed_roles = ["ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"user_id": "<user_id>", "title": "Order placed", "body": "Your order is being prepared", "data": {"order_id": "..."}}
    def post(self, request):
        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = {
            "user_id": serializer.validated_data.get("user_id"),
            "topic": serializer.validated_data.get("topic"),
            "title": serializer.validated_data["title"],
            "body": serializer.validated_data.get("body"),
            "data": serializer.validated_data.get("data"),
            "priority": serializer.validated_data.get("priority", "NORMAL"),
            "silent": serializer.validated_data.get("silent", False),
        }
        notif = services.enqueue_notification(payload)
        return Response({"notification": serialize_doc(notif)}, status=status.HTTP_202_ACCEPTED)


class ScheduleNotificationView(APIView):
    allowed_roles = ["ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"user_id": "<user_id>", "title": "Promo", "body": "Discount", "send_at": "2026-02-10T12:00:00Z"}
    def post(self, request):
        serializer = ScheduleNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = {
            "user_id": serializer.validated_data.get("user_id"),
            "topic": serializer.validated_data.get("topic"),
            "title": serializer.validated_data["title"],
            "body": serializer.validated_data.get("body"),
            "data": serializer.validated_data.get("data"),
            "priority": serializer.validated_data.get("priority", "NORMAL"),
            "silent": serializer.validated_data.get("silent", False),
        }
        notif = services.schedule_notification(payload, serializer.validated_data["send_at"])
        return Response({"notification": serialize_doc(notif)}, status=status.HTTP_201_CREATED)


class NotificationHistoryView(APIView):
    allowed_roles = ["ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        limit = int(request.query_params.get("limit", 50))
        notifications = services.list_notifications(limit=limit)
        return Response({"notifications": serialize_doc(notifications)})
