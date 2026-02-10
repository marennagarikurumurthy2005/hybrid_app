from rest_framework import serializers


class CouponApplySerializer(serializers.Serializer):
    code = serializers.CharField()
    amount = serializers.IntegerField(min_value=1)
    job_type = serializers.ChoiceField(choices=["ORDER", "RIDE"])


class ReferralUseSerializer(serializers.Serializer):
    referral_code = serializers.CharField()


class CampaignsQuerySerializer(serializers.Serializer):
    pass
