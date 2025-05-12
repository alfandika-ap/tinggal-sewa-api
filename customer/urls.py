from django.urls import path

from .views import CustomerLoginView, CustomerProfileView, CustomerRegisterView

urlpatterns = [
    path("register", CustomerRegisterView.as_view(), name="customer-register"),
    path("login", CustomerLoginView.as_view(), name="customer-login"),
    path("profile", CustomerProfileView.as_view(), name="customer-profile"),
]
