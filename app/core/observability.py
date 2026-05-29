from __future__ import annotations

import contextvars
import logging

_REQUEST_ID_CTX: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Inject request_id into every log record for structured correlation."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _REQUEST_ID_CTX.get("-")
        return True


def set_request_id(request_id: str) -> contextvars.Token[str]:
    return _REQUEST_ID_CTX.set(request_id)


def reset_request_id(token: contextvars.Token[str]) -> None:
    _REQUEST_ID_CTX.reset(token)


def get_request_id() -> str:
    return _REQUEST_ID_CTX.get("-")


def configure_logging() -> None:
    """Set a structured, request-id-aware logging format for app logs."""
    log_format = (
        "%(asctime)s level=%(levelname)s logger=%(name)s "
        "request_id=%(request_id)s message=\"%(message)s\""
    )

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        logging.basicConfig(level=logging.INFO, format=log_format)

    formatter = logging.Formatter(log_format)
    request_id_filter = RequestIdFilter()

    for handler in root_logger.handlers:
        handler.setFormatter(formatter)
        handler.addFilter(request_id_filter)

    # Keep HTTP client internals quieter in app logs.
    logging.getLogger("httpx").setLevel(logging.WARNING)
