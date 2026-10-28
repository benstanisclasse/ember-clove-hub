"""conversion events, daily counters, conversion settings

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-17
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PK = sa.BigInteger().with_variant(sa.Integer(), "sqlite")
SETTINGS = [
    (
        "conversions_enabled",
        False,
        "Send purchases and storefront events to Meta / TikTok / Google. Off until you turn it on.",
    ),
    (
        "conversions_hashed_pii",
        True,
        "Include SHA-256 hashed email + phone in purchase events (better matching). Raw values are never stored.",
    ),
    (
        "conversions_exclude_countries",
        [],
        'ISO country codes (billing) whose orders are never reported, e.g. ["DE", "FR"].',
    ),
]


def upgrade() -> None:
    op.create_table(
        "conversion_events",
        sa.Column("id", PK, nullable=False),
        sa.Column("platform", sa.String(16), nullable=False),
        sa.Column("event_name", sa.String(32), nullable=False),
        sa.Column("event_id", sa.String(128), nullable=False),
        sa.Column("order_id", PK, nullable=True),
        sa.Column("status", sa.String(16), nullable=False, comment="sent | failed | skipped"),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True, comment="skip reason or scrubbed error"),
        sa.Column("value", sa.Numeric(14, 2), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            name=op.f("fk_conversion_events_order_id_orders"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_conversion_events")),
        sa.UniqueConstraint(
            "platform",
            "event_name",
            "event_id",
            name=op.f("uq_conversion_events_platform_event_name_event_id"),
        ),
    )
    with op.batch_alter_table("conversion_events") as b:
        b.create_index(b.f("ix_conversion_events_order_id"), ["order_id"], unique=False)
        b.create_index(b.f("ix_conversion_events_sent_at"), ["sent_at"], unique=False)

    op.create_table(
        "conversion_event_counts",
        sa.Column("id", PK, nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("platform", sa.String(16), nullable=False, comment="hub = received"),
        sa.Column("event_name", sa.String(32), nullable=False),
        sa.Column("sent", sa.Integer(), nullable=False),
        sa.Column("failed", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_conversion_event_counts")),
        sa.UniqueConstraint(
            "date",
            "platform",
            "event_name",
            name=op.f("uq_conversion_event_counts_date_platform_event_name"),
        ),
    )

    settings = sa.table(
        "settings",
        sa.column("key", sa.String),
        sa.column("value", sa.JSON().with_variant(postgresql.JSONB(), "postgresql")),
        sa.column("description", sa.Text),
    )
    op.bulk_insert(settings, [{"key": k, "value": v, "description": d} for k, v, d in SETTINGS])


def downgrade() -> None:
    op.execute(
        "DELETE FROM settings WHERE key IN "
        "('conversions_enabled', 'conversions_hashed_pii', 'conversions_exclude_countries')"
    )
    op.drop_table("conversion_event_counts")
    with op.batch_alter_table("conversion_events") as b:
        b.drop_index(b.f("ix_conversion_events_sent_at"))
        b.drop_index(b.f("ix_conversion_events_order_id"))
    op.drop_table("conversion_events")
