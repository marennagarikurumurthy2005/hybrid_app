from django.urls import path
from routing import views

urlpatterns = [
    path("route/optimize/", views.RouteOptimizeView.as_view(), name="route-optimize"),
]
