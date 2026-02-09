from django.urls import path
from recommendations import views

urlpatterns = [
    path("recommendations/", views.UserRecommendationsView.as_view(), name="recommendations-list"),
    path("admin/recommendations/", views.AdminRecommendationListCreateView.as_view(), name="admin-recommendations"),
    path("admin/recommendations/<str:recommendation_id>/", views.AdminRecommendationDeleteView.as_view(), name="admin-recommendation-delete"),
]
