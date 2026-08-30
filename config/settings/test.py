from .base import *  # noqa

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "test_cozy_reads",
        "USER": env("POSTGRES_USER", default="cozy"),  # noqa: F405
        "PASSWORD": env("POSTGRES_PASSWORD", default="cozy"),  # noqa: F405
        "HOST": env("POSTGRES_HOST", default="localhost"),  # noqa: F405
        "PORT": env("POSTGRES_PORT", default="5432"),  # noqa: F405
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

MEDIA_ROOT = BASE_DIR / "test_media"  # noqa: F405
