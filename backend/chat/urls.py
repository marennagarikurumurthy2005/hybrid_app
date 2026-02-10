from django.urls import path
from chat import views

urlpatterns = [
    path("chat/history/<str:room_id>", views.ChatHistoryView.as_view(), name="chat-history"),
    path("chat/call/<str:room_id>", views.ChatMaskedCallView.as_view(), name="chat-call"),
    path("chat/read", views.ChatReadView.as_view(), name="chat-read"),
    path("chat/typing", views.ChatTypingView.as_view(), name="chat-typing"),
]
