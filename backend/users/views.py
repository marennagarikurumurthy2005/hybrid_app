from firebase_admin import auth as firebase_auth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from core.auth import create_access_token
from core.firebase import get_firebase_app
from core.utils import serialize_doc
from users.serializers import FirebaseLoginSerializer, FcmTokenSerializer, UserProfileUpdateSerializer
from users import services as user_services
from captains import services as captain_services


class FirebaseLoginView(APIView):
    permission_classes = [AllowAny]

    # Sample payload:
    # {
    #   "id_token": "<firebase_id_token>",
    #   "role": "USER"
    # }
    def post(self, request):
        serializer = FirebaseLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        id_token = serializer.validated_data["id_token"]
        requested_role = serializer.validated_data.get("role", "USER")

        firebase_app = get_firebase_app()
        decoded = firebase_auth.verify_id_token(id_token, app=firebase_app)

        phone = decoded.get("phone_number")
        if not phone and decoded.get("uid"):
            user_record = firebase_auth.get_user(decoded["uid"], app=firebase_app)
            phone = user_record.phone_number

        if not phone:
            return Response({"detail": "Phone number not found in token"}, status=status.HTTP_400_BAD_REQUEST)

        user_doc = user_services.get_user_by_phone(phone)
        if not user_doc:
            user_doc = user_services.create_user(phone=phone, role=requested_role)
        else:
            if not user_doc.get("role"):
                user_doc = user_services.update_role(str(user_doc["_id"]), requested_role)

        if user_doc.get("role") == "CAPTAIN":
            captain_services.ensure_captain_profile(str(user_doc["_id"]))

        token = create_access_token(user_doc)
        return Response({
            "token": token,
            "user": serialize_doc(user_doc),
        })


class MeView(APIView):
    def get(self, request):
        user_doc = getattr(request, "user_doc", None)
        if not user_doc:
            user_doc = user_services.get_user_by_id(request.user.id)
        return Response({"user": serialize_doc(user_doc)})

    # Thunder Client / Postman payload example:
    # {
    #   "name": "Asha Rao",
    #   "email": "asha@example.com",
    #   "avatar_url": "https://cdn.example.com/u/asha.png",
    #   "default_address": {"label": "Home", "line1": "MG Road"},
    #   "preferences": {"language": "en", "dark_mode": false}
    # }
    def patch(self, request):
        role = getattr(request.user, "role", None) or getattr(request, "role", None)
        if role != "USER":
            return Response({"detail": "Only USER can update this profile"}, status=status.HTTP_403_FORBIDDEN)

        payload = request.data or {}
        if not hasattr(payload, "keys"):
            return Response({"detail": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)

        requested = set(payload.keys())
        blocked = sorted({
            key for key in requested
            if key in user_services.USER_PROFILE_BLOCKED_FIELDS or str(key).startswith("_")
        })
        if blocked:
            return Response(
                {"detail": f"Updates to fields not allowed: {', '.join(blocked)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        filtered = {key: payload[key] for key in user_services.USER_PROFILE_EDITABLE_FIELDS if key in payload}
        if not filtered:
            return Response({"detail": "No valid fields to update"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserProfileUpdateSerializer(data=filtered, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = user_services.update_user_profile(request.user.id, serializer.validated_data)
        if not updated:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "success": True,
            "message": "Profile updated successfully",
            "data": serialize_doc(updated),
        })


class RegisterFcmTokenView(APIView):
    # Sample payload:
    # {
    #   "fcm_token": "<device_token>"
    # }
    def post(self, request):
        serializer = FcmTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = user_services.set_fcm_token(request.user.id, serializer.validated_data["fcm_token"])
        return Response({"user": serialize_doc(updated)})
