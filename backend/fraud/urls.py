from django.urls import path
from fraud import views

urlpatterns = [
    path("fraud/scan/", views.FraudScanView.as_view(), name="fraud-scan"),
]
