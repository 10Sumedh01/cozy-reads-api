import pytest

pytestmark = pytest.mark.django_db


class TestRegister:
    def test_register_creates_user(self, api_client):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "new@example.com",
                "username": "newuser",
                "password": "S3cure!Pass123",
                "password2": "S3cure!Pass123",
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.data["email"] == "new@example.com"

    def test_register_password_mismatch_fails(self, api_client):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "new2@example.com",
                "username": "newuser2",
                "password": "S3cure!Pass123",
                "password2": "Different!123",
            },
            format="json",
        )
        assert response.status_code == 400


class TestLogin:
    def test_login_success(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/login/",
            {
                "email": user.email,
                "password": "TestPass!123",
            },
            format="json",
        )
        assert response.status_code == 200
        assert "access" in response.data

    def test_login_wrong_password_fails(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/login/",
            {
                "email": user.email,
                "password": "wrong",
            },
            format="json",
        )
        assert response.status_code == 401


class TestMe:
    def test_me_requires_auth(self, api_client):
        response = api_client.get("/api/v1/auth/me/")
        assert response.status_code == 401

    def test_me_returns_profile(self, authenticated_client):
        client, user = authenticated_client
        response = client.get("/api/v1/auth/me/")
        assert response.status_code == 200
        assert response.data["email"] == user.email
