from rest_framework import serializers
from django.conf import settings


class FirebaseLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField()
    role = serializers.ChoiceField(choices=settings.ALLOWED_ROLES, required=False)


class FcmTokenSerializer(serializers.Serializer):
    fcm_token = serializers.CharField()


class UserProfileUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    avatar_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    default_address = serializers.JSONField(required=False, allow_null=True)
    preferences = serializers.JSONField(required=False, allow_null=True)
