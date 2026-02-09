from firebase_admin import auth as firebase_auth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from core.auth import create_access_token
from core.firebase import get_firebase_app
from core.utils import serialize_doc
from users.serializers import FirebaseLoginSerializer, FcmTokenSerializer
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
