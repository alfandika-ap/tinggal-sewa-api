from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from rest_framework import status, viewsets, filters
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Kost, Bookmark
from .serializers import (CustomerLoginSerializer, CustomerRegisterSerializer,
                          CustomerSerializer, KostSerializer, BookmarkSerializer)


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
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            customer_serializer = CustomerSerializer(user.customer)
            response_data = {
                "token": f"{token.key}",
                "customer": customer_serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerProfileView(APIView):
    """
    Get and update customer profile
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer = request.user.customer
        serializer = CustomerSerializer(customer)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def put(self, request):
        customer = request.user.customer
        print("Request data:", request.data)  # Debug log
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            print("Validated data:", serializer.validated_data)  # Debug log
            updated_customer = serializer.save()
            print("Updated customer:", updated_customer.fullname, updated_customer.phone, updated_customer.address)  # Debug log
            return Response(serializer.data, status=status.HTTP_200_OK)
        print("Serializer errors:", serializer.errors)  # Debug log
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookmarkViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing bookmarks
    """
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Return only bookmarks belonging to the authenticated user
        return Bookmark.objects.filter(user=self.request.user)
    
    def create(self, request):
        """
        Create a bookmark with kost data
        """
        # Extract kost data from request
        kost_data = {
            'title': request.data.get('title'),
            'address': request.data.get('address'),
            'city': request.data.get('city'),
            'province': request.data.get('province'),
            'description': request.data.get('description'),
            'price': float(request.data.get('price')),
            'contact': request.data.get('contact'),
            'url': request.data.get('url'),
            'gender': request.data.get('gender')
        }
        
        # Handle optional fields
        if 'image_url' in request.data:
            kost_data['image_url'] = request.data.get('image_url')
        
        # Get facilities and rules
        facilities = request.data.get('facilities', [])
        rules = request.data.get('rules', [])
        
        # Create the kost
        kost = Kost.objects.create(**kost_data)
        kost.set_facilities(facilities)
        kost.set_rules(rules)
        kost.save()
        
        # Check if bookmark already exists
        if Bookmark.objects.filter(user=request.user, kost=kost).exists():
            return Response({'error': 'A similar kost is already bookmarked'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Create the bookmark
        bookmark = Bookmark.objects.create(
            user=request.user,
            kost=kost
        )
        
        # Return the bookmark data
        serializer = self.get_serializer(bookmark)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# KostViewSet removed as requested
