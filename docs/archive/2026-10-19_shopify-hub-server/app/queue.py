"""Redis connection and RQ queues."""

from __future__ import annotations

from functools import lru_cache

from redis import Redis
from rq import Queue

from app.config import get_settings

QUEUES = ("high", "default", "low")


@lru_cache
def get_redis() -> Redis:
    return Redis.from_url(get_settings().redis_url, socket_timeout=5, socket_connect_timeout=5)


def get_queue(name: str = "default") -> Queue:
    if name not in QUEUES:
        raise ValueError(f"unknown queue {name!r}")
    return Queue(name, connection=get_redis(), default_timeout=1800)
