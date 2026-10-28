"""Named date ranges in the store's timezone, each with the equal-length previous period."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

NAMED = (
    "today",
    "yesterday",
    "last_7_days",
    "last_14_days",
    "last_30_days",
    "last_90_days",
    "this_month",
    "last_month",
)
_RANGE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:\.\.(\d{4}-\d{2}-\d{2}))?$")


@dataclass(frozen=True)
class Period:
    start: date
    end: date  # inclusive
    label: str

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1

    def previous(self) -> Period:
        end = self.start - timedelta(days=1)
        return Period(end - timedelta(days=self.days - 1), end, f"previous {self.days} days")

    def as_dict(self, tz: str) -> dict[str, str | int]:
        return {
            "label": self.label,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "days": self.days,
            "timezone": tz,
        }


def parse_period(value: str | None, tz: ZoneInfo, today: date | None = None) -> Period:
    """``last_7_days`` (default), ``yesterday``, ``this_month``, ``2026-10-01..2026-10-07``, ...

    "last_N_days" ends **yesterday** (complete days only); ``today`` is partial by nature.
    """
    today = today or datetime.now(tz).date()
    v = (value or "last_7_days").strip().lower()
    if v == "today":
        return Period(today, today, "today (partial)")
    if v == "yesterday":
        y = today - timedelta(days=1)
        return Period(y, y, "yesterday")
    if m := re.fullmatch(r"last_(\d+)_days", v):
        n = int(m.group(1))
        if not 1 <= n <= 730:
            raise ValueError("last_N_days: N must be 1..730")
        end = today - timedelta(days=1)
        return Period(end - timedelta(days=n - 1), end, f"last {n} complete days")
    if v == "this_month":
        return Period(today.replace(day=1), today, "this month to date")
    if v == "last_month":
        end = today.replace(day=1) - timedelta(days=1)
        return Period(end.replace(day=1), end, "last month")
    if m := _RANGE.match(v):
        start = date.fromisoformat(m.group(1))
        end = date.fromisoformat(m.group(2)) if m.group(2) else start
        if end < start:
            raise ValueError("period end is before start")
        if (end - start).days > 730:
            raise ValueError("period longer than 2 years")
        return Period(start, end, f"{start.isoformat()} to {end.isoformat()}")
    raise ValueError(
        f"unknown period {value!r}; use one of {', '.join(NAMED)}, last_N_days, or YYYY-MM-DD..YYYY-MM-DD"
    )
