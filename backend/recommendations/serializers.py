from rest_framework import serializers


class RecommendationCreateSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["RESTAURANT", "MENU_ITEM"])
    reference_id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
