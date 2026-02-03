from __future__ import annotations

import logging
import os
import sys

import structlog


def configure_structlog(log_level: str = "info"):
    """
    Minimal structlog configuration.

    - log_level: typically from env var LOG_LEVEL (info/debug/warning/error)
    - LOG_FORMAT env var:
        - "json" (default) -> JSON logs
        - "console"        -> pretty console logs
    """
    level_name = (log_level or "info").upper()
    level = getattr(logging, level_name, logging.INFO)

    # stdlib base config
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    root.addHandler(handler)

    log_format = os.getenv("LOG_FORMAT", "json").lower()
    renderer: structlog.types.Processor
    if log_format == "console":
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.add_log_level,
            structlog.processors.format_exc_info,
            renderer,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

