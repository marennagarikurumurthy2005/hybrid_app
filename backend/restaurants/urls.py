from django.urls import path
from restaurants import views

urlpatterns = [
    path("restaurants/", views.CreateRestaurantView.as_view(), name="restaurant-create"),
    path("restaurants/<str:restaurant_id>/menu/", views.AddMenuItemView.as_view(), name="menu-add"),
    path("restaurants/<str:restaurant_id>/menu/list/", views.ListMenuView.as_view(), name="menu-list"),
    path("restaurants/recommended/", views.RecommendedRestaurantsView.as_view(), name="restaurants-recommended"),
    path("menu/recommended/", views.RecommendedMenuItemsView.as_view(), name="menu-recommended"),
]
