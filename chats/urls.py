from django.urls import path

from .views import ChatHistoryView, ChatResetHistory, ChatView

urlpatterns = [
    path("streaming", ChatView.as_view(), name="chat-streaming"),
    path("history", ChatHistoryView.as_view(), name="chat-history"),
    path("reset", ChatResetHistory.as_view(), name="chat-reset"),
]
