"""creative metrics snapshots, bandit runs, ML model registry

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-18
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PK = sa.BigInteger().with_variant(sa.Integer(), "sqlite")
JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    op.create_table(
        "creative_metrics",
        sa.Column("id", PK, nullable=False),
        sa.Column("creative_id", PK, nullable=False),
        sa.Column("as_of", sa.Date(), nullable=False),
        sa.Column("window_days", sa.Integer(), nullable=False, comment="0 = lifetime"),
        sa.Column("spend", sa.Numeric(14, 2), nullable=False),
        sa.Column("impressions", sa.Integer(), nullable=False),
        sa.Column("clicks", sa.Integer(), nullable=False),
        sa.Column("video_3s_views", sa.Integer(), nullable=False),
        sa.Column("orders", sa.Numeric(10, 2), nullable=False),
        sa.Column("contribution_profit", sa.Numeric(14, 2), nullable=False),
        sa.Column("hook_rate", sa.Float(), nullable=True, comment="3s views / impressions"),
        sa.Column("ctr", sa.Float(), nullable=True, comment="clicks / impressions"),
        sa.Column("cpa", sa.Numeric(14, 2), nullable=True),
        sa.Column("profit_per_1000", sa.Numeric(14, 2), nullable=True),
        sa.Column("enough_data", sa.Boolean(), nullable=False),
        sa.Column(
            "verdict", sa.String(16), nullable=False, comment="learning | winner | loser | neutral"
        ),
        sa.ForeignKeyConstraint(
            ["creative_id"],
            ["creatives.id"],
            name=op.f("fk_creative_metrics_creative_id_creatives"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_creative_metrics")),
        sa.UniqueConstraint(
            "creative_id",
            "as_of",
            "window_days",
            name=op.f("uq_creative_metrics_creative_id_as_of_window_days"),
        ),
    )
    with op.batch_alter_table("creative_metrics") as b:
        b.create_index(b.f("ix_creative_metrics_creative_id"), ["creative_id"], unique=False)
        b.create_index(b.f("ix_creative_metrics_as_of"), ["as_of"], unique=False)

    op.create_table(
        "bandit_runs",
        sa.Column("id", PK, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("window_days", sa.Integer(), nullable=False),
        sa.Column("total_daily_budget", sa.Numeric(14, 2), nullable=False),
        sa.Column("arms", JSON, nullable=False, comment="per-platform estimates + shares"),
        sa.Column("proposals", JSON, nullable=True, comment="approval ids / skips"),
        sa.Column(
            "status", sa.String(16), nullable=False, comment="proposed | no_change | skipped"
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bandit_runs")),
    )
    with op.batch_alter_table("bandit_runs") as b:
        b.create_index(b.f("ix_bandit_runs_created_at"), ["created_at"], unique=False)

    op.create_table(
        "ml_models",
        sa.Column("id", PK, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("kind", sa.String(64), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, comment="active | inactive | retired"),
        sa.Column("n_labeled", sa.Integer(), nullable=False),
        sa.Column("metrics", JSON, nullable=True),
        sa.Column("features", JSON, nullable=True, comment="encoder vocabulary"),
        sa.Column("storage_key", sa.String(512), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ml_models")),
    )
    with op.batch_alter_table("ml_models") as b:
        b.create_index(b.f("ix_ml_models_kind"), ["kind"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("ml_models") as b:
        b.drop_index(b.f("ix_ml_models_kind"))
    op.drop_table("ml_models")
    with op.batch_alter_table("bandit_runs") as b:
        b.drop_index(b.f("ix_bandit_runs_created_at"))
    op.drop_table("bandit_runs")
    with op.batch_alter_table("creative_metrics") as b:
        b.drop_index(b.f("ix_creative_metrics_as_of"))
        b.drop_index(b.f("ix_creative_metrics_creative_id"))
    op.drop_table("creative_metrics")
