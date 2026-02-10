from django.urls import path
from vehicles import views

urlpatterns = [
    path("vehicle/register", views.VehicleRegisterView.as_view(), name="vehicle-register"),
    path("vehicle/rules", views.VehicleRulesView.as_view(), name="vehicle-rules"),
]
