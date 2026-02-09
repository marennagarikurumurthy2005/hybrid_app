from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from core.permissions import RolePermission
from core.utils import serialize_doc
from recommendations.serializers import RecommendationCreateSerializer
from recommendations import services


class AdminRecommendationListCreateView(APIView):
    allowed_roles = ["ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        recs = services.list_recommendations()
        return Response({"recommendations": serialize_doc(recs)})

    def post(self, request):
        serializer = RecommendationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            rec = services.create_recommendation(
                created_by=request.user.id,
                rec_type=serializer.validated_data["type"],
                reference_id=serializer.validated_data["reference_id"],
                title=serializer.validated_data["title"],
                description=serializer.validated_data.get("description"),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"recommendation": serialize_doc(rec)}, status=status.HTTP_201_CREATED)


class AdminRecommendationDeleteView(APIView):
    allowed_roles = ["ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    def delete(self, request, recommendation_id: str):
        try:
            services.delete_recommendation(recommendation_id)
        except ValueError as exc:
            detail = str(exc)
            status_code = status.HTTP_404_NOT_FOUND if "not found" in detail.lower() else status.HTTP_400_BAD_REQUEST
            return Response({"detail": detail}, status=status_code)
        return Response({"deleted": True})


class UserRecommendationsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        recs = services.list_user_recommendations()
        return Response({"recommendations": serialize_doc(recs)})
