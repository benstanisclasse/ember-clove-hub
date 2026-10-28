"""Normalize + SHA-256 hash customer identifiers the way Meta and TikTok require."""

from __future__ import annotations

import hashlib
import re


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_email(email: str | None) -> str | None:
    """Trim + lowercase, then hash. Returns None for empty / obviously invalid input."""
    if not email:
        return None
    e = email.strip().lower()
    return sha256(e) if "@" in e and "." in e.split("@")[-1] else None


def normalize_phone(phone: str | None, default_country_code: str = "1") -> str | None:
    """Digits only, with country code, no leading zeros or '+': '+1 (415) 555-0100' -> '14155550100'.

    Ten-digit numbers without a country code get ``default_country_code`` (US/CA: 1).
    """
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if phone.strip().startswith("00"):
        digits = digits[2:]
    digits = digits.lstrip("0")
    if len(digits) == 10:
        digits = default_country_code + digits
    return digits if 8 <= len(digits) <= 15 else None


def hash_phone(phone: str | None, default_country_code: str = "1") -> str | None:
    p = normalize_phone(phone, default_country_code)
    return sha256(p) if p else None


def hash_external_id(value: object) -> str | None:
    return sha256(str(value)) if value not in (None, "") else None
