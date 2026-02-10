from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.permissions import RolePermission
from core.utils import serialize_doc
from restaurant_ops.serializers import RestaurantOrderUpdateSerializer, RestaurantItemToggleSerializer
from restaurant_ops import services


class RestaurantOrderUpdateView(APIView):
    allowed_roles = ["RESTAURANT"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"order_id": "<order_id>", "status": "PREPARING", "prep_time_min": 20}
    def post(self, request):
        serializer = RestaurantOrderUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = services.update_order_status(
            serializer.validated_data["order_id"],
            serializer.validated_data["status"],
            serializer.validated_data.get("prep_time_min"),
        )
        if not order:
            return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"order": serialize_doc(order)})


class RestaurantItemToggleView(APIView):
    allowed_roles = ["RESTAURANT"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"menu_item_id": "<menu_item_id>", "is_available": false}
    def post(self, request):
        serializer = RestaurantItemToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = services.toggle_menu_item(
            serializer.validated_data["menu_item_id"],
            serializer.validated_data["is_available"],
        )
        if not item:
            return Response({"detail": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"menu_item": serialize_doc(item)})


class RestaurantAnalyticsView(APIView):
    allowed_roles = ["RESTAURANT"]
    permission_classes = [IsAuthenticated, RolePermission]

    def get(self, request):
        restaurant_id = request.query_params.get("restaurant_id")
        if not restaurant_id:
            return Response({"detail": "restaurant_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        data = services.get_analytics(restaurant_id)
        if not data:
            return Response({"detail": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"analytics": data})
