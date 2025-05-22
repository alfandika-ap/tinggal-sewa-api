from django.http import StreamingHttpResponse
from django.shortcuts import render
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from chats.tools import search_properties_metadata

from .methods import chat, search_properties
from .models import ChatMessages


class ChatMessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessages
        fields = ["id", "role", "content", "function_name", "created_at", "updated_at"]


class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = request.data.get("message")
        response = chat(message, request.user.id)
        return StreamingHttpResponse(response, content_type="text/event-stream")


class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        messages = ChatMessages.objects.filter(user=request.user)
        serializer = ChatMessagesSerializer(messages, many=True)
        return Response(serializer.data)


class ChatResetHistory(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ChatMessages.objects.filter(user=request.user).delete()
        return Response({"message": "History chat reset successfully"})

class SearchProperties(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get("query")
        metadata = request.data.get("metadata")
        response = search_properties(query, request.user.id, metadata)
        return Response(response)
    
class TestFunctionSearchProperties(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = search_properties_metadata(request.data.get("query"))
        return Response(response)
