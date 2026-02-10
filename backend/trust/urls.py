from django.urls import path
from trust import views

urlpatterns = [
    path("trust/device/register", views.DeviceRegisterView.as_view(), name="trust-device-register"),
    path("trust/scan", views.TrustScanView.as_view(), name="trust-scan"),
    path("trust/risk-score", views.RiskScoreView.as_view(), name="trust-risk-score"),
]
