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


class ChangePasswordSerializer(serializers.Serializer):
    """Used by an already-authenticated user who knows their current password."""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, label="Confirm new password")

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs.pop("new_password2"):
            raise serializers.ValidationError({"new_password2": "Passwords do not match."})
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Step 1 of the forgot-password flow: user submits their email."""

    email = serializers.EmailField()

    def validate_email(self, value):
        # Deliberately do NOT raise an error if the email isn't found — see
        # views.PasswordResetRequestView for why (avoids leaking which emails
        # are registered).
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Step 2: user submits the uid+token from their email, plus a new password."""

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, label="Confirm new password")

    def validate(self, attrs):
        if attrs["new_password"] != attrs.pop("new_password2"):
            raise serializers.ValidationError({"new_password2": "Passwords do not match."})
        return attrs
