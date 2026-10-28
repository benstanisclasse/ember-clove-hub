"""Structured logging with secret redaction.

All log output -- ours and third-party libraries' (uvicorn, SQLAlchemy, httpx, RQ) --
goes through the same structlog processor chain, which ends with :func:`redact`.
Redaction works on two levels:

* **by key**: any field whose name looks like a credential (``token``, ``secret``,
  ``authorization``, ``api_key`` ...) is replaced wholesale;
* **by value**: well-known token shapes (Shopify ``shpat_``, Meta ``EAA...``, Google
  ``ya29.`` / ``1//`` refresh tokens, ``Bearer ...``, ``access_token=`` query params,
  passwords in URLs, Slack webhook URLs) are masked wherever they appear, including
  inside exception tracebacks.
"""

from __future__ import annotations

import logging
import re
import sys
from collections.abc import Mapping, MutableMapping
from typing import Any

import structlog

REDACTED = "[REDACTED]"

_SENSITIVE_KEY = re.compile(
    r"(token|secret|password|passwd|authorization|api[_-]?key|cookie|hmac|signature|"
    r"credential|private[_-]?key)",
    re.IGNORECASE,
)

_VALUE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Shopify admin / shared-secret tokens
    (re.compile(r"\bshp(at|ss|ca|pa)_[A-Za-z0-9]{16,}"), REDACTED),
    # Meta long-lived / system-user tokens
    (re.compile(r"\bEAA[A-Za-z0-9]{20,}"), REDACTED),
    # Google OAuth access + refresh tokens
    (re.compile(r"\bya29\.[A-Za-z0-9_\-.]{10,}"), REDACTED),
    (re.compile(r"\b1//[A-Za-z0-9_\-]{20,}"), REDACTED),
    # Authorization headers
    (re.compile(r"(?i)\b(bearer|basic)\s+[A-Za-z0-9_\-.=+/]{8,}"), r"\1 " + REDACTED),
    # Secrets passed as query/form params
    (
        re.compile(
            r"(?i)\b(access_token|refresh_token|client_secret|api_key|apikey|token|"
            r"secret|password)=([^&\s\"']+)"
        ),
        r"\1=" + REDACTED,
    ),
    # Passwords embedded in URLs: scheme://user:pass@host
    (
        re.compile(r"([a-z][a-z0-9+\-.]*://[^:/@\s]+):[^@/\s]+@", re.IGNORECASE),
        r"\1:" + REDACTED + "@",
    ),
    # Slack incoming webhooks
    (
        re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/]+"),
        "https://hooks.slack.com/" + REDACTED,
    ),
]


def scrub(text: str) -> str:
    """Mask any token-shaped substrings in ``text``."""
    for pattern, replacement in _VALUE_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def _redact_value(key: str | None, value: Any) -> Any:
    if key is not None and _SENSITIVE_KEY.search(key) and value not in (None, "", False):
        return REDACTED
    if isinstance(value, str):
        return scrub(value)
    if isinstance(value, Mapping):
        return {k: _redact_value(str(k), v) for k, v in value.items()}
    if isinstance(value, list | tuple | set):
        return type(value)(_redact_value(None, v) for v in value)
    return value


def redact(
    _logger: Any, _method: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """structlog processor: redact credentials by key name and by value shape."""
    for key in list(event_dict.keys()):
        # Never treat the message itself as a sensitive *key*; still scrub its value.
        event_dict[key] = _redact_value(None if key == "event" else key, event_dict[key])
    return event_dict


def configure_logging(level: str = "INFO", json: bool = True) -> None:
    """Configure structlog + stdlib logging once per process."""
    shared: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        redact,  # last before rendering, so tracebacks are scrubbed too
    ]
    renderer: Any = (
        structlog.processors.JSONRenderer() if json else structlog.dev.ConsoleRenderer(colors=False)
    )

    structlog.configure(
        processors=[*shared, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                renderer,
            ],
        )
    )
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level.upper())

    # Chatty libraries: httpx logs full request URLs at INFO, which is where tokens hide.
    for noisy in ("httpx", "httpcore", "botocore", "boto3", "urllib3", "apscheduler.executors"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "rq.worker"):
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).propagate = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structured logger."""
    return structlog.get_logger(name)  # type: ignore[no-any-return]
