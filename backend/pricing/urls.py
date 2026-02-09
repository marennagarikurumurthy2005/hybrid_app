from django.urls import path
from pricing import views

urlpatterns = [
    path("pricing/calculate/", views.PricingCalculateView.as_view(), name="pricing-calc"),
]
