from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Customer, Kost, Bookmark


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


class KostSerializer(serializers.ModelSerializer):
    facilities = serializers.ListField(child=serializers.CharField(), required=False)
    rules = serializers.ListField(child=serializers.CharField(), required=False)
    
    class Meta:
        model = Kost
        fields = [
            'id', 'title', 'address', 'city', 'province', 'description',
            'price', 'facilities', 'rules', 'contact', 'url', 'image_url',
            'gender', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['facilities'] = instance.get_facilities()
        representation['rules'] = instance.get_rules()
        return representation
    
    def create(self, validated_data):
        facilities_data = validated_data.pop('facilities', [])
        rules_data = validated_data.pop('rules', [])
        
        kost = Kost.objects.create(**validated_data)
        kost.set_facilities(facilities_data)
        kost.set_rules(rules_data)
        kost.save()
        
        return kost
    
    def update(self, instance, validated_data):
        if 'facilities' in validated_data:
            facilities_data = validated_data.pop('facilities')
            instance.set_facilities(facilities_data)
        
        if 'rules' in validated_data:
            rules_data = validated_data.pop('rules')
            instance.set_rules(rules_data)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class BookmarkSerializer(serializers.ModelSerializer):
    kost = KostSerializer(read_only=True)
    title = serializers.CharField(write_only=True)
    address = serializers.CharField(write_only=True)
    city = serializers.CharField(write_only=True)
    province = serializers.CharField(write_only=True)
    description = serializers.CharField(write_only=True)
    price = serializers.FloatField(write_only=True)
    facilities = serializers.ListField(child=serializers.CharField(), write_only=True)
    rules = serializers.ListField(child=serializers.CharField(), write_only=True)
    contact = serializers.CharField(write_only=True)
    url = serializers.URLField(write_only=True)
    image_url = serializers.URLField(write_only=True, required=False, allow_null=True)
    gender = serializers.CharField(write_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Bookmark
        fields = [
            'id', 'user', 'username', 'kost', 'created_at',
            'title', 'address', 'city', 'province', 'description',
            'price', 'facilities', 'rules', 'contact', 'url', 'image_url', 'gender'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        # Extract kost data
        kost_data = {
            'title': validated_data.pop('title'),
            'address': validated_data.pop('address'),
            'city': validated_data.pop('city'),
            'province': validated_data.pop('province'),
            'description': validated_data.pop('description'),
            'price': validated_data.pop('price'),
            'contact': validated_data.pop('contact'),
            'url': validated_data.pop('url'),
            'gender': validated_data.pop('gender')
        }
        
        # Handle optional fields
        if 'image_url' in validated_data:
            kost_data['image_url'] = validated_data.pop('image_url')
            
        # Get facilities and rules
        facilities_data = validated_data.pop('facilities', [])
        rules_data = validated_data.pop('rules', [])
        
        # Create the kost
        kost = Kost.objects.create(**kost_data)
        kost.set_facilities(facilities_data)
        kost.set_rules(rules_data)
        kost.save()
        
        # Get the user from the context
        user = self.context['request'].user
        
        # Check if bookmark already exists
        if Bookmark.objects.filter(user=user, kost=kost).exists():
            raise serializers.ValidationError({'error': 'A similar kost is already bookmarked'})
        
        # Create the bookmark
        bookmark = Bookmark.objects.create(
            user=user,
            kost=kost
        )
        
        return bookmark
