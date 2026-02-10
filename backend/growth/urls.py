from django.urls import path
from growth import views

urlpatterns = [
    path("feed/personalized", views.PersonalizedFeedView.as_view(), name="feed-personalized"),
    path("experiment/assign", views.ExperimentAssignView.as_view(), name="experiment-assign"),
]
