from rest_framework.views import APIView
from rest_framework.response import Response

from notifications.serializers import SendNotificationSerializer
from notifications import services


class SendNotificationView(APIView):
    # Sample payload:
    # {"user_id": "<user_id>", "title": "Order placed", "body": "Your order is being prepared", "data": {"order_id": "..."}}
    def post(self, request):
        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sent = services.send_to_user(
            serializer.validated_data["user_id"],
            serializer.validated_data["title"],
            serializer.validated_data["body"],
            serializer.validated_data.get("data"),
        )
        return Response({"sent": sent})
