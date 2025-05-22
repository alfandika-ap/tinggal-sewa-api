from django.urls import path

from .views import ChatHistoryView, ChatResetHistory, ChatView, SearchProperties, TestFunctionSearchProperties

urlpatterns = [
    path("streaming", ChatView.as_view(), name="chat-streaming"),
    path("history", ChatHistoryView.as_view(), name="chat-history"),
    path("reset", ChatResetHistory.as_view(), name="chat-reset"),
    path("search-properties", SearchProperties.as_view(), name="property-search"),
    path("test-search-properties", TestFunctionSearchProperties.as_view(), name="test-property-search"),
]
