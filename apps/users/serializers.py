from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """Validates and creates a new user. Password is write-only and never echoed back."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label="Confirm password")

    class Meta:
        model = User
        fields = ["email", "username", "password", "password2", "mobile", "gender"]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        # create_user() hashes the password; never assign to .password directly.
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Used for GET/PATCH /auth/me/. Identity fields are read-only; profile fields are editable."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "mobile",
            "gender",
            "profile_pic",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "email", "username", "created_at", "updated_at"]
