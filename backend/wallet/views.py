from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.utils import serialize_doc
from core.permissions import RolePermission
from wallet.serializers import WalletRefundSerializer
from wallet import services


class WalletTransactionsView(APIView):
    def get(self, request):
        txns = services.list_transactions(request.user.id)
        return Response({"transactions": serialize_doc(txns)})


class WalletRefundView(APIView):
    allowed_roles = ["USER"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"reference": "<order_id>", "amount": 5000, "reason": "Order cancelled", "source": "FOOD"}
    def post(self, request):
        serializer = WalletRefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        txn = services.refund_wallet(
            request.user.id,
            serializer.validated_data["amount"],
            serializer.validated_data["reason"],
            serializer.validated_data["source"],
            reference=serializer.validated_data.get("reference"),
        )
        if not txn:
            return Response({"detail": "Refund failed"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"transaction": serialize_doc(txn)})
