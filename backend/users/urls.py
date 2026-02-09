from django.urls import path
from users import views

urlpatterns = [
    path("auth/firebase/", views.FirebaseLoginView.as_view(), name="firebase-login"),
    path("users/me/", views.MeView.as_view(), name="me"),
    path("users/fcm-token/", views.RegisterFcmTokenView.as_view(), name="register-fcm"),
]
