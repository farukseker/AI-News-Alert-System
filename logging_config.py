import logging
import structlog
import json
from datetime import datetime
from typing import List, Dict, Optional
from collections import deque
from config import get_settings


settings = get_settings()

LOG_BUFFER_SIZE = 1000
log_buffer: deque = deque(maxlen=LOG_BUFFER_SIZE)


class LogBufferHandler:
    def __call__(self, logger, method_name, event_dict):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": method_name.upper(),
            "event": event_dict.pop("event", ""),
            "image_id": event_dict.pop("image_id", None),
            "task_id": event_dict.pop("task_id", None),
            "message": event_dict.pop("msg", None),
            "meta": event_dict if event_dict else None,
        }
        log_buffer.append(log_entry)
        return event_dict

def get_log_buffer() -> List[Dict]:
    return list(log_buffer)

def configure_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            LogBufferHandler(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        # logger_factory=structlog.PrintLoggerFactory(),
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