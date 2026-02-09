from django.urls import path
from rides import views

urlpatterns = [
    path("rides/fare/", views.RideFareView.as_view(), name="ride-fare"),
    path("rides/", views.RideCreateView.as_view(), name="ride-create"),
    path("rides/verify-payment/", views.RideVerifyPaymentView.as_view(), name="ride-verify"),
    path("rides/complete/", views.RideCompleteView.as_view(), name="ride-complete"),
]
