from rest_framework import serializers
from django.conf import settings


class FirebaseLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField()
    role = serializers.ChoiceField(choices=settings.ALLOWED_ROLES, required=False)


class FcmTokenSerializer(serializers.Serializer):
    fcm_token = serializers.CharField()
