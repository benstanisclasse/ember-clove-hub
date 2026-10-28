"""MCP OAuth clients/tokens, approvals_via_mcp setting

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-18
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    op.create_table(
        "oauth_clients",
        sa.Column("client_id", sa.String(512), nullable=False),
        sa.Column("client_name", sa.String(255), nullable=True),
        sa.Column("redirect_uris", JSON, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("revoked", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("client_id", name=op.f("pk_oauth_clients")),
    )
    op.create_table(
        "oauth_tokens",
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False, comment="code | access | refresh"),
        sa.Column("client_id", sa.String(512), nullable=False),
        sa.Column("scope", sa.String(255), nullable=True),
        sa.Column("redirect_uri", sa.Text(), nullable=True),
        sa.Column("code_challenge", sa.String(128), nullable=True),
        sa.Column("resource", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("token_hash", name=op.f("pk_oauth_tokens")),
    )
    with op.batch_alter_table("oauth_tokens") as b:
        b.create_index(b.f("ix_oauth_tokens_client_id"), ["client_id"], unique=False)
        b.create_index(b.f("ix_oauth_tokens_expires_at"), ["expires_at"], unique=False)

    settings = sa.table(
        "settings",
        sa.column("key", sa.String),
        sa.column("value", JSON),
        sa.column("description", sa.Text),
    )
    op.bulk_insert(
        settings,
        [
            {
                "key": "approvals_via_mcp",
                "value": True,
                "description": "Allow approving proposals through Claude (approve_action tool). "
                "Off = approve only via the admin API/CLI.",
            }
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM settings WHERE key = 'approvals_via_mcp'")
    with op.batch_alter_table("oauth_tokens") as b:
        b.drop_index(b.f("ix_oauth_tokens_expires_at"))
        b.drop_index(b.f("ix_oauth_tokens_client_id"))
    op.drop_table("oauth_tokens")
    op.drop_table("oauth_clients")
