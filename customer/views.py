from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .serializers import CustomerRegisterSerializer, CustomerLoginSerializer, CustomerSerializer


class CustomerRegisterView(APIView):
    """
    Register a new customer
    """
    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            response_serializer = CustomerSerializer(customer)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerLoginView(APIView):
    """
    Login for customers
    """
    def post(self, request):
        serializer = CustomerLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Get or create token
            token, created = Token.objects.get_or_create(user=user)
            
            # Get customer profile
            customer_serializer = CustomerSerializer(user.customer)
            
            # Return token and customer data
            response_data = {
                'token': f"{token.key}",
                'customer': customer_serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class CustomerProfileView(APIView):
    """
    Get customer profile
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        customer = request.user.customer
        serializer = CustomerSerializer(customer)
        return Response(serializer.data, status=status.HTTP_200_OK)
