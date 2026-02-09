from django.urls import path
from ratings import views

urlpatterns = [
    path("captain/rate/", views.CaptainRateView.as_view(), name="captain-rate"),
    path("captain/<str:captain_id>/stats/", views.CaptainStatsView.as_view(), name="captain-stats"),
]
