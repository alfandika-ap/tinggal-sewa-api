from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CustomerLoginView, CustomerProfileView, CustomerRegisterView,
    BookmarkViewSet
)

# Create a router for viewsets
router = DefaultRouter()
router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')

urlpatterns = [
    path("register", CustomerRegisterView.as_view(), name="customer-register"),
    path("login", CustomerLoginView.as_view(), name="customer-login"),
    path("profile", CustomerProfileView.as_view(), name="customer-profile"),
    # Include the router URLs
    path("", include(router.urls)),
]
