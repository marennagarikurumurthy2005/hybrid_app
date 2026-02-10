from django.urls import path
from restaurant_ops import views

urlpatterns = [
    path("restaurant/order/update", views.RestaurantOrderUpdateView.as_view(), name="restaurant-order-update"),
    path("restaurant/item/toggle", views.RestaurantItemToggleView.as_view(), name="restaurant-item-toggle"),
    path("restaurant/analytics", views.RestaurantAnalyticsView.as_view(), name="restaurant-analytics"),
]
