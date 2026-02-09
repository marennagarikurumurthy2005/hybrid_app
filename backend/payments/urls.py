from django.urls import path
from payments import views

urlpatterns = [
    path("payments/razorpay/order/", views.RazorpayCreateOrderView.as_view(), name="razorpay-order"),
    path("payments/razorpay/verify/", views.RazorpayVerifyView.as_view(), name="razorpay-verify"),
]
