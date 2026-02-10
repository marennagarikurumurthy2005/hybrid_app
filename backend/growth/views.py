from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import RolePermission
from core.utils import serialize_doc
from growth.serializers import ExperimentAssignSerializer
from growth import services


class PersonalizedFeedView(APIView):
    allowed_roles = ["USER"]
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        limit = int(request.query_params.get("limit", 50))
        feed = services.personalized_feed(request.user.id, limit=limit)
        return Response({"feed": serialize_doc(feed)})


class ExperimentAssignView(APIView):
    allowed_roles = ["USER", "ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"experiment_key": "homepage_v1", "variants": ["A", "B"]}
    def post(self, request):
        serializer = ExperimentAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            assignment = services.assign_experiment(
                request.user.id,
                serializer.validated_data["experiment_key"],
                serializer.validated_data["variants"],
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"assignment": assignment})
