from django.urls import path
from promotions import views

urlpatterns = [
    path("coupon/apply", views.CouponApplyView.as_view(), name="coupon-apply"),
    path("referral/use", views.ReferralUseView.as_view(), name="referral-use"),
    path("campaigns/active", views.ActiveCampaignsView.as_view(), name="campaigns-active"),
]
