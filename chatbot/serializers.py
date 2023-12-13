from rest_framework import serializers
from .models import Chat, User
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = (
            "id",
            "message",
            "response",
            "created_at",
        )

class RegistrationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "phone",
            "password",
        ]
       