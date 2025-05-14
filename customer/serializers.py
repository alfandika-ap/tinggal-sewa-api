from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Customer


class CustomerRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    fullname = serializers.CharField(max_length=255, required=True)
    phone = serializers.CharField(max_length=255, required=True)
    address = serializers.CharField(required=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        customer = Customer.objects.create(
            user=user,
            fullname=validated_data["fullname"],
            phone=validated_data["phone"],
            address=validated_data["address"],
        )
        return customer


class CustomerLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not hasattr(user, "customer"):
                    raise serializers.ValidationError("User is not a customer")
                data["user"] = user
            else:
                raise serializers.ValidationError(
                    "Unable to login with provided credentials"
                )
        else:
            raise serializers.ValidationError("Must provide username and password")

        return data


class CustomerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    email = serializers.EmailField(source="user.email")

    class Meta:
        model = Customer
        fields = [
            "id",
            "username",
            "email",
            "fullname",
            "phone",
            "address",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        
    def update(self, instance, validated_data):
        # Update user fields
        user_data = validated_data.pop('user', {})
        if user_data:
            user = instance.user
            if 'username' in user_data:
                user.username = user_data['username']
            if 'email' in user_data:
                user.email = user_data['email']
            user.save()
            
        # Update customer fields
        instance.fullname = validated_data.get('fullname', instance.fullname)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.address = validated_data.get('address', instance.address)
        instance.save()
        return instance
