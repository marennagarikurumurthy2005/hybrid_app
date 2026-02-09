from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from core.permissions import RolePermission
from core.utils import serialize_doc, to_object_id
from restaurants.serializers import RestaurantCreateSerializer, MenuItemCreateSerializer
from restaurants import services


class CreateRestaurantView(APIView):
    allowed_roles = ["RESTAURANT"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"name": "Biryani House", "address": "MG Road", "phone": "+919999999999", "lat": 12.97, "lng": 77.59}
    def post(self, request):
        serializer = RestaurantCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        restaurant = services.create_restaurant(
            owner_id=request.user.id,
            name=serializer.validated_data["name"],
            address=serializer.validated_data.get("address"),
            phone=serializer.validated_data.get("phone"),
            lat=serializer.validated_data.get("lat"),
            lng=serializer.validated_data.get("lng"),
        )
        return Response({"restaurant": serialize_doc(restaurant)}, status=status.HTTP_201_CREATED)


class AddMenuItemView(APIView):
    allowed_roles = ["RESTAURANT"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"name": "Chicken Biryani", "price": 25000, "is_available": true}
    def post(self, request, restaurant_id: str):
        serializer = MenuItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        restaurant = services.get_restaurant(restaurant_id)
        if not restaurant:
            return Response({"detail": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)
        if restaurant.get("owner_id") != to_object_id(request.user.id):
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        item = services.add_menu_item(
            restaurant_id=restaurant_id,
            name=serializer.validated_data["name"],
            price=serializer.validated_data["price"],
            is_available=serializer.validated_data.get("is_available", True),
        )
        return Response({"menu_item": serialize_doc(item)}, status=status.HTTP_201_CREATED)


class ListMenuView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, restaurant_id: str):
        items = services.list_menu_items(restaurant_id)
        return Response({"items": serialize_doc(items)})
