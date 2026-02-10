from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.permissions import RolePermission
from eta.serializers import EtaPredictSerializer
from eta import services


class EtaPredictView(APIView):
    allowed_roles = ["USER", "CAPTAIN", "RESTAURANT", "ADMIN"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"origin_lat": 12.97, "origin_lng": 77.59, "destination_lat": 12.93, "destination_lng": 77.61, "prep_time_min": 15}
    def post(self, request):
        serializer = EtaPredictSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = services.predict_eta(serializer.validated_data)
        return Response({"eta": result})
