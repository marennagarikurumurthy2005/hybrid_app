from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from core.permissions import RolePermission
from core.utils import serialize_doc, to_object_id
from restaurants.serializers import RestaurantCreateSerializer, MenuItemCreateSerializer, RestaurantProfileUpdateSerializer
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


class RecommendedRestaurantsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        limit = int(request.query_params.get("limit", 50))
        restaurants = services.list_recommended_restaurants(limit=limit)
        return Response({"restaurants": serialize_doc(restaurants)})


class RecommendedMenuItemsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        limit = int(request.query_params.get("limit", 50))
        items = services.list_recommended_menu_items(limit=limit)
        return Response({"items": serialize_doc(items)})


class RestaurantMeView(APIView):
    allowed_roles = ["RESTAURANT"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Thunder Client / Postman payload example:
    # {
    #   "name": "Biryani House",
    #   "logo_url": "https://cdn.example.com/brands/biryani.png",
    #   "address": "MG Road",
    #   "opening_time": "09:00",
    #   "closing_time": "23:00",
    #   "is_open": true,
    #   "support_phone": "+919999999999"
    # }
    def patch(self, request):
        payload = request.data or {}
        if not hasattr(payload, "keys"):
            return Response({"detail": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)

        requested = set(payload.keys())
        blocked = sorted({
            key for key in requested
            if key in services.RESTAURANT_PROFILE_BLOCKED_FIELDS or str(key).startswith("_")
        })
        if blocked:
            return Response(
                {"detail": f"Updates to fields not allowed: {', '.join(blocked)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        filtered = {key: payload[key] for key in services.RESTAURANT_PROFILE_EDITABLE_FIELDS if key in payload}
        if not filtered:
            return Response({"detail": "No valid fields to update"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RestaurantProfileUpdateSerializer(data=filtered, partial=True)
        serializer.is_valid(raise_exception=True)

        restaurant = services.get_restaurant_by_owner(request.user.id)
        if not restaurant:
            return Response({"detail": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)
        if "support_phone" in serializer.validated_data:
            verified = bool(
                restaurant.get("is_verified")
                or restaurant.get("support_phone_verified")
            )
            if not verified:
                return Response(
                    {"detail": "support_phone can be updated only after verification"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        updated = services.update_restaurant_profile(request.user.id, serializer.validated_data)
        if not updated:
            return Response({"detail": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "success": True,
            "message": "Profile updated successfully",
            "data": serialize_doc(updated),
        })
