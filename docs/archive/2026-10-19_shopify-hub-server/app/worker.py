"""RQ worker process: ``python -m app.worker``."""

from __future__ import annotations

from rq import Worker

from app.config import get_settings
from app.log import configure_logging, get_logger
from app.queue import QUEUES, get_queue, get_redis


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_json)
    get_logger(__name__).info("worker_starting", queues=list(QUEUES))
    worker = Worker([get_queue(q) for q in QUEUES], connection=get_redis())
    # with_scheduler: RQ's own scheduler runs delayed jobs (enqueue_in), e.g. purchases
    # sent a couple of minutes after the order so the browser signals have arrived.
    worker.work(with_scheduler=True, logging_level=settings.log_level.upper())


if __name__ == "__main__":
    main()
