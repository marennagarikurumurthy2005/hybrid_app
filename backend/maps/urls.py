from django.urls import path
from maps import views

urlpatterns = [
    path("maps/route", views.MapsRouteView.as_view(), name="maps-route"),
    path("maps/eta", views.MapsEtaView.as_view(), name="maps-eta"),
    path("captain/nearby", views.NearbyCaptainsView.as_view(), name="captain-nearby"),
]
