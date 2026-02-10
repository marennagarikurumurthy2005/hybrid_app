from django.urls import path
from observability import views

urlpatterns = [
    path("health", views.HealthView.as_view(), name="health"),
    path("metrics", views.MetricsView.as_view(), name="metrics"),
]
