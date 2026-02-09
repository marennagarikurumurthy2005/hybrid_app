from django.urls import path
from notifications import views

urlpatterns = [
    path("notifications/send/", views.SendNotificationView.as_view(), name="notifications-send"),
]
