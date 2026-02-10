from firebase_admin import auth as firebase_auth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from core.auth import create_access_token, create_refresh_token, decode_token, blacklist_token, is_token_blacklisted
from core.firebase import get_firebase_app
from core.utils import serialize_doc
from users.serializers import (
    FirebaseLoginSerializer,
    FcmTokenSerializer,
    UserProfileUpdateSerializer,
    RefreshTokenSerializer,
    LogoutSerializer,
    UserAddressCreateSerializer,
    UserAddressUpdateSerializer,
    FavoriteCreateSerializer,
)
from users import services as user_services
from captains import services as captain_services
from core.permissions import RolePermission
from core.geo_utils import to_point


def _get_ip_address(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or "unknown"


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
        device_id = serializer.validated_data.get("device_id") or request.headers.get("X-Device-Id")
        device_name = serializer.validated_data.get("device_name") or request.headers.get("X-Device-Name")

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
        refresh_token = create_refresh_token(user_doc)
        refresh_payload = decode_token(refresh_token, verify_type="refresh")
        user_services.create_session(
            str(user_doc["_id"]),
            refresh_payload.get("jti"),
            refresh_token,
            device_id=device_id,
            device_name=device_name,
            user_agent=request.META.get("HTTP_USER_AGENT"),
            ip_address=_get_ip_address(request),
        )
        return Response({
            "token": token,
            "refresh_token": refresh_token,
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


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    # Sample payload:
    # {"refresh_token": "<refresh_jwt>"}
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh_token"]
        try:
            payload = decode_token(refresh_token, verify_type="refresh")
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)

        jti = payload.get("jti")
        if is_token_blacklisted(jti):
            return Response({"detail": "Refresh token revoked"}, status=status.HTTP_401_UNAUTHORIZED)

        session = user_services.get_session_by_refresh_jti(jti)
        if not session or session.get("revoked_at"):
            return Response({"detail": "Session revoked"}, status=status.HTTP_401_UNAUTHORIZED)

        user_doc = user_services.get_user_by_id(payload.get("sub"))
        if not user_doc:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        new_refresh_token = create_refresh_token(user_doc)
        new_refresh_payload = decode_token(new_refresh_token, verify_type="refresh")
        user_services.rotate_session(jti, new_refresh_payload.get("jti"), new_refresh_token)
        blacklist_token(jti, "refresh", payload.get("sub"), payload.get("exp"))

        access_token = create_access_token(user_doc)
        return Response({
            "token": access_token,
            "refresh_token": new_refresh_token,
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    # Sample payload:
    # {"refresh_token": "<refresh_jwt>"}
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data.get("refresh_token") or ""

        auth = request.META.get("HTTP_AUTHORIZATION", "")
        access_token = auth.split(" ", 1)[1] if auth.startswith("Bearer ") else ""

        if access_token:
            try:
                access_payload = decode_token(access_token, verify_type="access")
                blacklist_token(
                    access_payload.get("jti"),
                    "access",
                    access_payload.get("sub"),
                    access_payload.get("exp"),
                )
            except Exception:
                pass

        if refresh_token:
            try:
                refresh_payload = decode_token(refresh_token, verify_type="refresh")
                user_services.revoke_session(refresh_payload.get("jti"), reason="LOGOUT")
                blacklist_token(
                    refresh_payload.get("jti"),
                    "refresh",
                    refresh_payload.get("sub"),
                    refresh_payload.get("exp"),
                )
            except Exception:
                pass

        return Response({"success": True})


class UserSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = user_services.list_sessions(request.user.id, include_revoked=False)
        return Response({"sessions": serialize_doc(sessions)})


class UserAddressListCreateView(APIView):
    allowed_roles = ["USER"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {
    #   "label": "HOME",
    #   "line1": "MG Road",
    #   "city": "Bengaluru",
    #   "lat": 12.9716,
    #   "lng": 77.5946,
    #   "is_default": true
    # }
    def post(self, request):
        serializer = UserAddressCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        location = None
        if data.get("lat") is not None and data.get("lng") is not None:
            location = to_point(data["lat"], data["lng"])
        address = user_services.create_user_address(
            request.user.id,
            data,
            location=location,
        )
        return Response({"address": serialize_doc(address)}, status=status.HTTP_201_CREATED)

    def get(self, request):
        addresses = user_services.list_user_addresses(request.user.id)
        return Response({"addresses": serialize_doc(addresses)})


class UserAddressDetailView(APIView):
    allowed_roles = ["USER"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"label": "WORK", "is_default": false}
    def patch(self, request, address_id: str):
        serializer = UserAddressUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        location = None
        if "lat" in data or "lng" in data:
            if data.get("lat") is not None and data.get("lng") is not None:
                location = to_point(data["lat"], data["lng"])
            else:
                location = None
        updated = user_services.update_user_address(
            request.user.id,
            address_id,
            data,
            location=location,
        )
        if not updated:
            return Response({"detail": "Address not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"address": serialize_doc(updated)})

    def delete(self, request, address_id: str):
        deleted = user_services.delete_user_address(request.user.id, address_id)
        if not deleted:
            return Response({"detail": "Address not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"deleted": True})


class FavoriteCreateView(APIView):
    allowed_roles = ["USER"]
    permission_classes = [IsAuthenticated, RolePermission]

    # Sample payload:
    # {"favorite_type": "RESTAURANT", "reference_id": "<restaurant_id>"}
    def post(self, request):
        serializer = FavoriteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        favorite = user_services.add_favorite(
            request.user.id,
            serializer.validated_data["favorite_type"],
            serializer.validated_data["reference_id"],
        )
        return Response({"favorite": serialize_doc(favorite)}, status=status.HTTP_201_CREATED)
