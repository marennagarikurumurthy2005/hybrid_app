from rest_framework import serializers


class SendNotificationSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    title = serializers.CharField()
    body = serializers.CharField()
    data = serializers.DictField(required=False)
