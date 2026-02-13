import logging
import sys
import structlog
from datetime import datetime
from typing import List, Dict
from collections import deque

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from config import get_settings


settings = get_settings()

LOG_BUFFER_SIZE = 1000
log_buffer: deque = deque(maxlen=LOG_BUFFER_SIZE)


class LogBufferHandler:
    def __call__(self, logger, method_name, event_dict):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": method_name.upper(),
            "event": event_dict.get("event"),
            "image_id": event_dict.get("image_id"),
            "task_id": event_dict.get("task_id"),
            "message": event_dict.get("msg"),
            "meta": {
                k: v for k, v in event_dict.items()
                if k not in {"event", "image_id", "task_id", "msg"}
            } or None,
        }
        log_buffer.append(log_entry)
        return event_dict


class SentryProcessor:
    """
    Forwards structlog events to Sentry.
    - ERROR and above: captured as Sentry events.
    - WARNING and below: added as Sentry breadcrumbs.
    """

    SENTRY_LEVELS = {"critical", "error"}
    BREADCRUMB_LEVELS = {"warning", "info", "debug"}

    def __call__(self, logger, method_name, event_dict):
        level = method_name.lower()
        event_msg = event_dict.get("event", "")

        exc_info = event_dict.pop("exc_info", None)
        exception = event_dict.pop("exception", None)

        extra = {
            k: v for k, v in event_dict.items()
            if k not in {"timestamp", "level", "_logger", "_name"}
        }

        if level in self.SENTRY_LEVELS:
            with sentry_sdk.push_scope() as scope:
                for key, value in extra.items():
                    scope.set_extra(key, value)

                if exc_info is True:
                    current_exc_info = sys.exc_info()
                    if current_exc_info[1] is not None:
                        sentry_sdk.capture_exception(current_exc_info[1])
                    else:
                        sentry_sdk.capture_message(event_msg, level=level)
                elif exc_info and isinstance(exc_info, tuple):
                    if exc_info[1] is not None:
                        sentry_sdk.capture_exception(exc_info[1])
                    else:
                        sentry_sdk.capture_message(event_msg, level=level)
                elif isinstance(exception, BaseException):
                    sentry_sdk.capture_exception(exception)
                else:
                    sentry_sdk.capture_message(event_msg, level=level)

        elif level in self.BREADCRUMB_LEVELS:
            sentry_sdk.add_breadcrumb(
                message=event_msg,
                level=level,
                data=extra,
            )

        return event_dict


def get_log_buffer() -> List[Dict]:
    return list(log_buffer)


def configure_sentry():
    sentry_logging = LoggingIntegration(
        level=logging.WARNING,
        event_level=None,
    )

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        integrations=[sentry_logging],
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=True,
    )


def configure_logging():
    configure_sentry()

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            LogBufferHandler(),
            SentryProcessor(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.LOG_LEVEL),
    )


def get_logger(name: str):
    return structlog.get_logger(name)


logger = get_logger(__name__)

__all__ = "get_logger", "configure_logging"