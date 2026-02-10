from django.urls import path
from cancellation import views

urlpatterns = [
    path("cancel/policy", views.CancelPolicyView.as_view(), name="cancel-policy"),
    path("cancel/order", views.CancelOrderView.as_view(), name="cancel-order"),
    path("cancel/ride", views.CancelRideView.as_view(), name="cancel-ride"),
]
