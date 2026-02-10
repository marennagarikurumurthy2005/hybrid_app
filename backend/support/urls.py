from django.urls import path
from support import views

urlpatterns = [
    path("support/ticket", views.SupportTicketCreateView.as_view(), name="support-ticket"),
]
