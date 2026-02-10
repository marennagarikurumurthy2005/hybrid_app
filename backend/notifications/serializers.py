from rest_framework import serializers


class SendNotificationSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=False)
    topic = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField()
    body = serializers.CharField(required=False, allow_blank=True)
    data = serializers.DictField(required=False)
    priority = serializers.ChoiceField(choices=["LOW", "NORMAL", "HIGH"], required=False, default="NORMAL")
    silent = serializers.BooleanField(required=False, default=False)


class ScheduleNotificationSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=False)
    topic = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField()
    body = serializers.CharField(required=False, allow_blank=True)
    data = serializers.DictField(required=False)
    priority = serializers.ChoiceField(choices=["LOW", "NORMAL", "HIGH"], required=False, default="NORMAL")
    silent = serializers.BooleanField(required=False, default=False)
    send_at = serializers.DateTimeField()
