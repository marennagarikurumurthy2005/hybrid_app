from django.urls import path
from orders import views

urlpatterns = [
    path("orders/checkout/", views.OrderCheckoutView.as_view(), name="order-checkout"),
    path("orders/", views.OrderCreateView.as_view(), name="order-create"),
    path("orders/verify-payment/", views.OrderVerifyPaymentView.as_view(), name="order-verify"),
]
