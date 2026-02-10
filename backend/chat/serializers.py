from rest_framework import serializers


class ChatSendSerializer(serializers.Serializer):
    room_id = serializers.CharField()
    message = serializers.CharField()
    receiver_id = serializers.CharField(required=False, allow_blank=True)
    receiver_role = serializers.CharField(required=False, allow_blank=True)
    client_message_id = serializers.CharField(required=False, allow_blank=True)


class ChatHistorySerializer(serializers.Serializer):
    limit = serializers.IntegerField(required=False, min_value=1, max_value=200)


class ChatReceiptSerializer(serializers.Serializer):
    message_id = serializers.CharField()


class ChatReadSerializer(serializers.Serializer):
    room_id = serializers.CharField()
    message_id = serializers.CharField(required=False, allow_blank=True)


class ChatTypingSerializer(serializers.Serializer):
    room_id = serializers.CharField()
    is_typing = serializers.BooleanField()
