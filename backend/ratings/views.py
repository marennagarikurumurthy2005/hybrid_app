from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import RolePermission
from core.utils import serialize_doc
from ratings.serializers import CaptainRateSerializer
from ratings import services


class CaptainRateView(APIView):
    allowed_roles = ["USER"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"job_type": "RIDE", "job_id": "<ride_id>", "rating": 5, "comment": "Great ride"}
    def post(self, request):
        serializer = CaptainRateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            rating_doc = services.rate_captain(
                request.user.id,
                serializer.validated_data["job_type"],
                serializer.validated_data["job_id"],
                serializer.validated_data["rating"],
                serializer.validated_data.get("comment"),
            )
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"rating": serialize_doc(rating_doc)}, status=status.HTTP_201_CREATED)


class CaptainStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, captain_id: str):
        stats = services.get_captain_stats(captain_id)
        if not stats:
            return Response({"detail": "Captain not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"stats": stats})
