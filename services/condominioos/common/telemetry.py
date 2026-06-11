"""Structured logging + tracing setup. Logs are PII-scrubbed and carry tenant + trace ids."""

from __future__ import annotations

import logging
import sys

import structlog


def configure_telemetry(service: str) -> None:
    """Configure structlog for JSON structured logs. OTel tracing wired at app startup."""
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            _scrub_pii,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )
    structlog.get_logger().info("telemetry.configured", service=service)


# Keys that must never appear in plain logs.
_PII_KEYS = {"email", "phone", "fiscal_code", "iban", "full_name", "address", "body"}


def _scrub_pii(_logger: object, _method: str, event_dict: dict) -> dict:
    for key in list(event_dict):
        if key.lower() in _PII_KEYS:
            event_dict[key] = "[redacted]"
    return event_dict


def get_logger(name: str) -> structlog.BoundLogger:
    return structlog.get_logger(name)
