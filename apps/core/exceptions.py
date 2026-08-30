import logging

from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Wraps DRF's default handler to produce a consistent error envelope:
    { "error": { "detail": ..., "code": ... } }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_payload = {
            "error": {
                "detail": response.data.get("detail", response.data)
                if isinstance(response.data, dict)
                else response.data,
                "status_code": response.status_code,
            }
        }
        response.data = error_payload
    else:
        logger.exception("Unhandled exception", exc_info=exc)

    return response
