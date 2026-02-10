from rest_framework import serializers


class SupportTicketSerializer(serializers.Serializer):
    subject = serializers.CharField()
    message = serializers.CharField()
    category = serializers.CharField(required=False, allow_blank=True)
    priority = serializers.ChoiceField(choices=["LOW", "NORMAL", "HIGH"], required=False)
