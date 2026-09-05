# Cozy Reads API

Welcome to the **Cozy Reads API**, a production-ready Django and Django REST Framework (DRF) backend. This document serves as a developer guide to help you understand the project structure, Django/DRF architecture, and how to get started.

---

## 1. Project Directory Structure

The repository is modular and structured as follows:

```text
cozy-reads-api/
├── manage.py                  # Django CLI entrypoint for running servers, migrations, etc.
├── pytest.ini                 # Pytest configuration
├── docker-compose.yml         # Local development environment container definitions
├── requirements/              # Dependency files split by environment
│   ├── base.txt               # Shared packages (Django, DRF, Celery, SimpleJWT)
│   ├── local.txt              # Local packages (Debug Toolbar, Pytest)
│   └── production.txt         # Production packages (Gunicorn, Boto3, Sentry-SDK)
├── config/                    # Global Settings and Centralized Routing
│   ├── settings/              # Settings modularized per environment
│   │   ├── base.py            # Global and default configurations
│   │   ├── local.py           # Settings for local development
│   │   ├── test.py            # Settings optimized for test suite
│   │   └── production.py      # Production-hardened configurations
│   ├── urls.py                # Core URL router mapping top-level endpoints
│   └── api_v1_urls.py         # Sub-routing that bundles all app APIs under /api/v1/
├── docker/                    # Dockerfiles and container configurations (Nginx, Celery, Django)
└── apps/                      # Custom Applications (Domain Logic)
    ├── core/                  # Shared exceptions, utility views, health probes, and helper base classes
    ├── users/                 # Custom User Model, authentication (JWT), and user profile management
    ├── books/                 # Google Books Integration, search, metadata
    ├── library/               # User personal reading libraries, collections, read status
    ├── epub/                  # EPUB parser, upload, and chapter index processing
    ├── goals/                 # Annual and monthly reading goals
    └── stats/                 # Aggregated analytics, charts, and reading habits
```

---

## 2. Core Django & Django REST Framework (DRF) Architecture

Traditional Django uses the **Model-View-Template (MVT)** pattern. Since this project is a headless API backend, we replace the HTML Templates with **DRF Serializers**, adopting a clean **Model-Serializer-View** pattern.

```
[Client Request] ──> [URL Routing] ──> [View] ──> [Serializer] ──> [Model] ──> [Database]
[Client Response] <── [Custom Exceptions/Payload] <── [Serializer] <───┘
```

### Key Components:

1. **Models (`apps/<app_name>/models.py`)**
   * Represents your database schema using Django’s Object-Relational Mapper (ORM).
   * Models are translated to SQL migrations dynamically via `python manage.py makemigrations`.
   * *Example:* `apps/users/models.py` extends Django's standard authentication user class with fields like `gender`, `mobile`, and `profile_pic`.

2. **Serializers (`apps/<app_name>/serializers.py`)**
   * They behave as the **validators** and **translators** of your API.
   * **Deserialization (Incoming)**: Takes client-submitted JSON data, runs validation logic (e.g. matching passwords), and maps them into Python model instances.
   * **Serialization (Outgoing)**: Translates database rows/Python structures back into formatted JSON responses.

3. **Views (`apps/<app_name>/views.py`)**
   * Acts as the controller. Determines permissions (who can access it), handles HTTP verbs (`GET`, `POST`, `PATCH`, `DELETE`), and uses serializers to process data.
   * Leverages DRF's generic classes (like `CreateAPIView` or `RetrieveUpdateAPIView`) to minimize boilerplate code.

4. **URLs Routing (`apps/<app_name>/urls.py` & `config/urls.py`)**
   * Maps specific HTTP endpoints to the correct views.

---

## 3. The DRF Request/Response Lifecycle (Example: Creating a User)

1. **Routing:** Client sends a `POST` request to `/api/v1/auth/register/` with email and password.
2. **View Routing:** Django matches this path in `config/urls.py` -> `config/api_v1_urls.py` -> `apps/users/urls.py` and maps it to `RegisterView`.
3. **Authentication/Permission check:** View checks if the caller matches requirements. Since `RegisterView` allows anonymous access (`permissions.AllowAny`), the request is approved.
4. **Validation (Serializer):** View hands the payload over to `RegisterSerializer`.
   * It checks password strength.
   * It verifies that `password` and `password2` are identical.
   * If any check fails, DRF automatically returns `HTTP 400 Bad Request` with structured errors.
5. **Database Mutation:** If data is valid, the serializer's `create` method is executed. It invokes `User.objects.create_user()` to hash the password and save the record in PostgreSQL.
6. **Response Envelope:** The view intercepts the result and delegates back to the custom exception or response formatter to deliver the final response to the client.

---

## 4. Key Infrastructure Features

* **JSON Web Token (JWT) Security**: Authentication uses `SimpleJWT` (`/api/v1/auth/login/` and `/api/v1/auth/logout/`). Clients send an `Authorization: Bearer <token>` header with subsequent requests.
* **Global Error Envelope**: Modified at `apps/core/exceptions.py` to intercept errors, guaranteeing all API exceptions strictly conform to a nested error layout:
  ```json
  {
    "error": {
      "detail": "Descriptive error message",
      "status_code": 400
    }
  }
  ```
* **Health Checks**: A special `/health/` endpoint checks connection to both PostgreSQL and Redis caches to support container orchestrators (Docker/Kubernetes).
* **Background Tasks**: Celery is preconfigured to handle long-running operations (like parsing EPUBs or sending digest emails) outside the request-response loop.

---

## 5. Local Setup Checklist

1. **Environment Setup:**
   Copy the example environment file and customize as needed:
   ```bash
   cp .env.example .env
   ```

2. **Run Containers (PostgreSQL, Redis, Django, Celery):**
   ```bash
   docker-compose up --build
   ```

3. **Run Migrations & Create Superuser:**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Verify API Docs:**
   Access the interactive Swagger documentation in your browser:
   * **Swagger UI**: [http://localhost:8000/docs/](http://localhost:8000/docs/)
   * **OpenAPI Schema**: [http://localhost:8000/schema/](http://localhost:8000/schema/)
