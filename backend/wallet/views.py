from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.utils import serialize_doc
from core.permissions import RolePermission
from wallet.serializers import WalletRefundSerializer, WalletSettleSerializer
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


class WalletLedgerView(APIView):
    def get(self, request):
        limit = int(request.query_params.get("limit", 50))
        entries = services.list_ledger_entries(request.user.id, limit=limit)
        return Response({"entries": serialize_doc(entries)})


class WalletSettleView(APIView):
    allowed_roles = ["ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"limit": 50}
    def post(self, request):
        serializer = WalletSettleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        limit = serializer.validated_data.get("limit", 50)
        settled = services.run_settlements(limit=limit)
        return Response({"settled": serialize_doc(settled)})
