from django.shortcuts import render
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from .methods import chat
from .models import ChatMessages
from rest_framework.permissions import IsAuthenticated

class ChatMessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessages
        fields = ['id', 'role', 'content', 'created_at', 'updated_at']

class ChatView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        message = request.data.get('message')
        response = chat(message, request.user.id)
        return StreamingHttpResponse(response, content_type='text/event-stream')

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