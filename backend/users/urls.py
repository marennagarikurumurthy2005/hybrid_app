from django.urls import path
from users import views

urlpatterns = [
    path("auth/firebase/", views.FirebaseLoginView.as_view(), name="firebase-login"),
    path("auth/refresh", views.RefreshTokenView.as_view(), name="auth-refresh"),
    path("auth/logout", views.LogoutView.as_view(), name="auth-logout"),
    path("users/me/", views.MeView.as_view(), name="me"),
    path("users/sessions", views.UserSessionsView.as_view(), name="user-sessions"),
    path("users/fcm-token/", views.RegisterFcmTokenView.as_view(), name="register-fcm"),
    path("users/address", views.UserAddressListCreateView.as_view(), name="user-address-list"),
    path("users/address/<str:address_id>", views.UserAddressDetailView.as_view(), name="user-address-detail"),
    path("favorites", views.FavoriteCreateView.as_view(), name="favorite-create"),
]
