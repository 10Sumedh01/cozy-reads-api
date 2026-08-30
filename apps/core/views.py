from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse


def health_check(request):
    """Checks DB + Redis connectivity. Used by Docker/K8s readiness probes."""
    status = {"status": "ok", "db": "ok", "cache": "ok"}
    http_status = 200

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        status["db"] = "error"
        status["status"] = "error"
        http_status = 503

    try:
        cache.set("health_check", "1", timeout=5)
        cache.get("health_check")
    except Exception:
        status["cache"] = "error"
        status["status"] = "error"
        http_status = 503

    return JsonResponse(status, status=http_status)
