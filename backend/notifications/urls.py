from django.urls import path
from notifications import views

urlpatterns = [
    path("notify/send", views.SendNotificationView.as_view(), name="notify-send"),
    path("notify/schedule", views.ScheduleNotificationView.as_view(), name="notify-schedule"),
    path("notify/history", views.NotificationHistoryView.as_view(), name="notify-history"),
]
