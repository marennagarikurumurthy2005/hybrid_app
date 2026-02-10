from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import RolePermission
from core.utils import serialize_doc
from payouts.serializers import PayoutRequestSerializer, BankLinkSerializer
from payouts import services


class CaptainEarningsView(APIView):
    allowed_roles = ["CAPTAIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        wallet = services.get_wallet(request.user.id)
        return Response({"wallet": serialize_doc(wallet)})


class CaptainPayoutRequestView(APIView):
    allowed_roles = ["CAPTAIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"amount": 5000}
    def post(self, request):
        serializer = PayoutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payout = services.request_payout(request.user.id, serializer.validated_data["amount"])
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"payout": serialize_doc(payout)}, status=status.HTTP_201_CREATED)


class CaptainPayoutHistoryView(APIView):
    allowed_roles = ["CAPTAIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        limit = int(request.query_params.get("limit", 50))
        payouts = services.list_payouts(request.user.id, limit=limit)
        return Response({"payouts": serialize_doc(payouts)})


class CaptainBankLinkView(APIView):
    allowed_roles = ["CAPTAIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"account_number": "1234567890", "ifsc": "HDFC0001234", "name": "Captain", "upi": "captain@upi"}
    def post(self, request):
        serializer = BankLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bank = services.link_bank_account(
            request.user.id,
            serializer.validated_data["account_number"],
            serializer.validated_data["ifsc"],
            serializer.validated_data["name"],
            serializer.validated_data.get("upi"),
        )
        if not bank:
            return Response({"detail": "Invalid captain"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"bank_account": serialize_doc(bank)})
