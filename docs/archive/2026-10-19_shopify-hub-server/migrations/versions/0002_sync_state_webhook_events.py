"""sync state cursors and webhook events

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-17
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    op.create_table(
        "sync_state",
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("value", JSON, nullable=True),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("key", name=op.f("pk_sync_state")),
    )
    op.create_table(
        "webhook_events",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False, comment="shopify | ..."),
        sa.Column("topic", sa.String(length=64), nullable=False),
        sa.Column("delivery_id", sa.String(length=128), nullable=False),
        sa.Column("resource_id", sa.String(length=128), nullable=True),
        sa.Column("payload_sha256", sa.String(length=64), nullable=True),
        sa.Column(
            "received_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            sa.String(length=16),
            nullable=False,
            comment="received|processed|ignored|failed",
        ),
        sa.Column("error", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_webhook_events")),
        sa.UniqueConstraint("delivery_id", name=op.f("uq_webhook_events_delivery_id")),
    )
    with op.batch_alter_table("webhook_events") as batch_op:
        batch_op.create_index(batch_op.f("ix_webhook_events_topic"), ["topic"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_webhook_events_received_at"), ["received_at"], unique=False
        )


def downgrade() -> None:
    with op.batch_alter_table("webhook_events") as batch_op:
        batch_op.drop_index(batch_op.f("ix_webhook_events_received_at"))
        batch_op.drop_index(batch_op.f("ix_webhook_events_topic"))
    op.drop_table("webhook_events")
    op.drop_table("sync_state")
