from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import (ChangePasswordSerializer,
                          PasswordResetConfirmSerializer,
                          PasswordResetRequestSerializer, RegisterSerializer,
                          UserSerializer)


class RegisterView(generics.CreateAPIView):
    """POST /auth/register/ — anyone can create an account."""

    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class LoginView(TokenObtainPairView):
    """
    POST /auth/login/ — email + password in, {access, refresh} tokens out.
    Subclassed only to attach a throttle scope (brute-force protection);
    all the actual auth logic is simplejwt's built-in TokenObtainPairView.
    """

    throttle_scope = "login"


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {"refresh": {"type": "string"}},
        }
    }
)
class LogoutView(APIView):
    """POST /auth/logout/ — blacklists the given refresh token so it can't be reused."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "Invalid or already-blacklisted token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_205_RESET_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /auth/me/ — the logged-in user's own profile."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


@extend_schema(request=ChangePasswordSerializer)
class ChangePasswordView(APIView):
    """POST /auth/change-password/ — logged-in user changes their own password."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password updated successfully."})


@extend_schema(request=PasswordResetRequestSerializer)
class PasswordResetRequestView(APIView):
    """
    POST /auth/password-reset/ — anyone can call this with an email.
    Always returns 200 with a generic message, whether or not that email
    is registered — this stops the endpoint being used to enumerate accounts.
    """

    permission_classes = [permissions.AllowAny]
    throttle_scope = "password-reset"

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        user = User.objects.filter(email__iexact=email).first()
        if user is not None:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            # In production this becomes a link into the frontend, e.g.
            # f"https://cozyreads.app/reset-password?uid={uid}&token={token}"
            send_mail(
                subject="Reset your Cozy Reads password",
                message=(
                    "Use these values with POST /api/v1/auth/password-reset/confirm/ "
                    f"to set a new password:\nuid={uid}\ntoken={token}\n\n"
                    "This link expires and can only be used once."
                ),
                from_email=None,  # uses settings.DEFAULT_FROM_EMAIL
                recipient_list=[user.email],
            )

        return Response(
            {"detail": "If that email is registered, a reset link has been sent."}
        )


@extend_schema(request=PasswordResetConfirmSerializer)
class PasswordResetConfirmView(APIView):
    """POST /auth/password-reset/confirm/ — sets a new password using the uid+token from email."""

    permission_classes = [permissions.AllowAny]
    throttle_scope = "password-reset-confirm"

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            uid = force_str(urlsafe_base64_decode(data["uid"]))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            user = None

        if user is None or not default_token_generator.check_token(user, data["token"]):
            return Response(
                {"detail": "This reset link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(data["new_password"])
        user.save(update_fields=["password"])
        return Response({"detail": "Password has been reset. You can now log in."})
