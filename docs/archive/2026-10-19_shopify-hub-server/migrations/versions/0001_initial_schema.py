"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-10-17 18:09:14.744669
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# --- Contribution-profit views ---------------------------------------------------------
# Same formulas as app/profit.py (tests check they agree). Written in portable SQL so the
# test suite can run them on SQLite as well as Postgres. "* 1.0" forces non-integer
# division on SQLite; on Postgres it is a no-op on NUMERIC.

V_ORDER_PROFIT = """
CREATE VIEW v_order_profit AS
WITH item_costs AS (
    SELECT
        oi.order_id,
        SUM(oi.quantity * COALESCE(oi.unit_cost, v.unit_cost, p.unit_cost, 0)) AS cogs,
        SUM(oi.quantity * COALESCE(v.shipping_cost, p.shipping_cost, 0)) AS est_shipping_cost,
        SUM(oi.quantity) AS units,
        SUM(CASE WHEN COALESCE(oi.unit_cost, v.unit_cost, p.unit_cost) IS NULL
                 THEN oi.quantity ELSE 0 END) AS units_missing_cost
    FROM order_items oi
    LEFT JOIN product_variants v ON v.id = oi.variant_id
    LEFT JOIN products p ON p.id = COALESCE(oi.product_id, v.product_id)
    GROUP BY oi.order_id
)
SELECT
    o.id AS order_id,
    o.shopify_id,
    o.order_date,
    o.currency,
    o.customer_id,
    o.is_first_order,
    o.attributed_platform,
    o.attributed_campaign_id,
    o.attributed_ad_id,
    o.attribution_method,
    (o.total_price - o.total_tax) AS net_revenue,
    o.total_discounts AS discounts,
    (o.total_refunded - o.refunded_tax) AS refunds,
    COALESCE(ic.cogs, 0) AS cogs,
    COALESCE(o.shipping_cost, ic.est_shipping_cost, 0) AS shipping_cost,
    o.payment_fees,
    (o.total_price - o.total_tax)
      - (o.total_refunded - o.refunded_tax)
      - COALESCE(ic.cogs, 0)
      - COALESCE(o.shipping_cost, ic.est_shipping_cost, 0)
      - o.payment_fees AS contribution_profit,
    COALESCE(ic.units, 0) AS units,
    COALESCE(ic.units_missing_cost, 0) AS units_missing_cost
FROM orders o
LEFT JOIN item_costs ic ON ic.order_id = o.id
WHERE o.cancelled_at IS NULL AND NOT o.test
"""

V_AD_DAILY_PROFIT = """
CREATE VIEW v_ad_daily_profit AS
WITH attributed AS (
    SELECT attributed_ad_id AS ad_id, order_date AS date,
           COUNT(*) AS orders,
           SUM(net_revenue) AS net_revenue,
           SUM(contribution_profit) AS contribution
    FROM v_order_profit
    WHERE attributed_ad_id IS NOT NULL
    GROUP BY attributed_ad_id, order_date
), ad_days AS (
    SELECT ad_id, date FROM ad_metrics_daily
    UNION
    SELECT ad_id, date FROM attributed
)
SELECT
    k.ad_id,
    k.date,
    a.platform,
    COALESCE(m.spend, 0) AS spend,
    COALESCE(m.impressions, 0) AS impressions,
    COALESCE(m.clicks, 0) AS clicks,
    COALESCE(m.video_3s_views, 0) AS video_3s_views,
    COALESCE(m.add_to_cart, 0) AS add_to_cart,
    COALESCE(m.purchases, 0) AS platform_purchases,
    COALESCE(m.platform_revenue, 0) AS platform_revenue,
    COALESCE(att.orders, 0) AS attributed_orders,
    COALESCE(att.net_revenue, 0) AS attributed_revenue,
    COALESCE(att.contribution, 0) AS attributed_contribution,
    COALESCE(att.contribution, 0) - COALESCE(m.spend, 0) AS contribution_profit
FROM ad_days k
JOIN ads a ON a.id = k.ad_id
LEFT JOIN ad_metrics_daily m ON m.ad_id = k.ad_id AND m.date = k.date
LEFT JOIN attributed att ON att.ad_id = k.ad_id AND att.date = k.date
"""

V_CREATIVE_DAILY_PROFIT = """
CREATE VIEW v_creative_daily_profit AS
WITH link_counts AS (
    SELECT ad_id, COUNT(*) AS n FROM creative_ad_links GROUP BY ad_id
)
SELECT
    l.creative_id,
    p.date,
    SUM(p.spend * 1.0 / lc.n) AS spend,
    SUM(p.impressions * 1.0 / lc.n) AS impressions,
    SUM(p.clicks * 1.0 / lc.n) AS clicks,
    SUM(p.video_3s_views * 1.0 / lc.n) AS video_3s_views,
    SUM(p.attributed_orders * 1.0 / lc.n) AS attributed_orders,
    SUM(p.attributed_revenue * 1.0 / lc.n) AS attributed_revenue,
    SUM(p.attributed_contribution * 1.0 / lc.n) AS attributed_contribution,
    SUM(p.contribution_profit * 1.0 / lc.n) AS contribution_profit
FROM creative_ad_links l
JOIN link_counts lc ON lc.ad_id = l.ad_id
JOIN v_ad_daily_profit p ON p.ad_id = l.ad_id
GROUP BY l.creative_id, p.date
"""

# Frozen copy of the defaults in app/business_settings.py at the time of this migration.
SETTINGS_SEED = [
    ("read_only", True, "When true, every write action is blocked. Starts true."),
    (
        "kill_switch",
        False,
        "Emergency stop: blocks all write actions regardless of other settings.",
    ),
    (
        "daily_spend_cap",
        None,
        "Max total daily ad budget across platforms (store currency). null = not set; spend increases blocked.",
    ),
    ("max_budget_change_pct", 20.0, "Max % change to any single budget per day."),
    ("max_new_ads_per_day", 5, "Max ads the hub may create per day."),
    (
        "higgsfield_monthly_cap_usd",
        None,
        "Max Higgsfield spend per calendar month (USD). null = not set; generation blocked.",
    ),
    (
        "auto_approve_rules",
        [],
        "List of rules that let matching proposals skip the approval queue.",
    ),
]


def upgrade() -> None:
    op.create_table(
        "ad_accounts",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column(
            "platform",
            sa.Enum(
                "google",
                "meta",
                "tiktok",
                name="platform",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("external_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("timezone", sa.String(length=64), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "paused",
                "pending_review",
                "rejected",
                "archived",
                "deleted",
                "unknown",
                name="entity_status",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ad_accounts")),
        sa.UniqueConstraint(
            "platform", "external_id", name=op.f("uq_ad_accounts_platform_external_id")
        ),
    )
    op.create_table(
        "customers",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column("shopify_id", sa.BigInteger(), nullable=False),
        sa.Column("first_order_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_order_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("order_count", sa.Integer(), nullable=False),
        sa.Column("total_revenue", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_customers")),
        sa.UniqueConstraint("shopify_id", name=op.f("uq_customers_shopify_id")),
    )
    op.create_table(
        "job_runs",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column("job_name", sa.String(length=128), nullable=False),
        sa.Column(
            "started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "running",
                "success",
                "failed",
                name="job_run_status",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "stats",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_job_runs")),
    )
    with op.batch_alter_table("job_runs", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_job_runs_job_name"), ["job_name"], unique=False)

    op.create_table(
        "pending_approvals",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("action_type", sa.String(length=64), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False, comment="One-line human summary"),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column(
            "payload",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column("requested_by", sa.String(length=255), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "approved",
                "rejected",
                "expired",
                "executed",
                "failed",
                name="approval_status",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("auto_approved", sa.Boolean(), nullable=False),
        sa.Column("auto_approve_rule", sa.String(length=128), nullable=True),
        sa.Column("decided_by", sa.String(length=255), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "result",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_pending_approvals")),
    )
    with op.batch_alter_table("pending_approvals", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_pending_approvals_status"), ["status"], unique=False)

    op.create_table(
        "products",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column("shopify_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("handle", sa.String(length=255), nullable=True),
        sa.Column("product_type", sa.String(length=255), nullable=True),
        sa.Column(
            "price",
            sa.Numeric(precision=14, scale=2),
            nullable=True,
            comment="Lowest variant price",
        ),
        sa.Column(
            "unit_cost", sa.Numeric(precision=14, scale=2), nullable=True, comment="COGS per unit"
        ),
        sa.Column(
            "shipping_cost",
            sa.Numeric(precision=14, scale=2),
            nullable=True,
            comment="Our fulfilment cost per unit (not what the customer pays)",
        ),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("shopify_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_products")),
        sa.UniqueConstraint("shopify_id", name=op.f("uq_products_shopify_id")),
    )
    op.create_table(
        "settings",
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column(
            "value",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("updated_by", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("key", name=op.f("pk_settings")),
    )
    op.create_table(
        "actions_log",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "actor",
            sa.String(length=32),
            nullable=False,
            comment="mcp | scheduler | worker | admin | cli | system",
        ),
        sa.Column("requested_by", sa.String(length=255), nullable=True, comment="Client / user id"),
        sa.Column("tool", sa.String(length=128), nullable=True, comment="MCP tool name, if any"),
        sa.Column("action_type", sa.String(length=64), nullable=False),
        sa.Column("target_type", sa.String(length=64), nullable=True),
        sa.Column("target_id", sa.String(length=128), nullable=True),
        sa.Column(
            "payload",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
        sa.Column(
            "approval_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=True
        ),
        sa.Column("approved_by", sa.String(length=255), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "success",
                "failed",
                "blocked",
                "pending_approval",
                "dry_run",
                name="action_status",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "result",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["approval_id"],
            ["pending_approvals.id"],
            name=op.f("fk_actions_log_approval_id_pending_approvals"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_actions_log")),
    )
    with op.batch_alter_table("actions_log", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_actions_log_action_type"), ["action_type"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_actions_log_approval_id"), ["approval_id"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_actions_log_created_at"), ["created_at"], unique=False)

    op.create_table(
        "campaigns",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column(
            "ad_account_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column(
            "platform",
            sa.Enum(
                "google",
                "meta",
                "tiktok",
                name="platform",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("external_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=512), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "paused",
                "pending_review",
                "rejected",
                "archived",
                "deleted",
                "unknown",
                name="entity_status",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("objective", sa.String(length=64), nullable=True),
        sa.Column("daily_budget", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("lifetime_budget", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["ad_account_id"],
            ["ad_accounts.id"],
            name=op.f("fk_campaigns_ad_account_id_ad_accounts"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_campaigns")),
        sa.UniqueConstraint(
            "platform", "external_id", name=op.f("uq_campaigns_platform_external_id")
        ),
    )
    with op.batch_alter_table("campaigns", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_campaigns_ad_account_id"), ["ad_account_id"], unique=False
        )

    op.create_table(
        "creatives",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "video",
                "image",
                name="creative_type",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "draft",
                "generating",
                "ready",
                "failed",
                "approved",
                "launched",
                "archived",
                name="creative_status",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "storage_key", sa.String(length=1024), nullable=True, comment="Object key in bucket"
        ),
        sa.Column("storage_url", sa.Text(), nullable=True),
        sa.Column("mime_type", sa.String(length=64), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("higgsfield_model", sa.String(length=128), nullable=True),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column(
            "brief",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
        sa.Column("duration_seconds", sa.Numeric(precision=7, scale=2), nullable=True),
        sa.Column("cost_usd", sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column(
            "parent_creative_id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "product_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=True
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["parent_creative_id"],
            ["creatives.id"],
            name=op.f("fk_creatives_parent_creative_id_creatives"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_creatives_product_id_products"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_creatives")),
    )
    with op.batch_alter_table("creatives", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_creatives_parent_creative_id"), ["parent_creative_id"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_creatives_product_id"), ["product_id"], unique=False)

    op.create_table(
        "product_variants",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column(
            "product_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("shopify_id", sa.BigInteger(), nullable=False),
        sa.Column("sku", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=512), nullable=True),
        sa.Column("price", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("unit_cost", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("shipping_cost", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_product_variants_product_id_products"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_product_variants")),
        sa.UniqueConstraint("shopify_id", name=op.f("uq_product_variants_shopify_id")),
    )
    with op.batch_alter_table("product_variants", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_product_variants_product_id"), ["product_id"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_product_variants_sku"), ["sku"], unique=False)

    op.create_table(
        "ad_sets",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column(
            "campaign_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column(
            "platform",
            sa.Enum(
                "google",
                "meta",
                "tiktok",
                name="platform",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("external_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=512), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "paused",
                "pending_review",
                "rejected",
                "archived",
                "deleted",
                "unknown",
                name="entity_status",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("daily_budget", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("lifetime_budget", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("optimization_goal", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["campaign_id"],
            ["campaigns.id"],
            name=op.f("fk_ad_sets_campaign_id_campaigns"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ad_sets")),
        sa.UniqueConstraint(
            "platform", "external_id", name=op.f("uq_ad_sets_platform_external_id")
        ),
    )
    with op.batch_alter_table("ad_sets", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_ad_sets_campaign_id"), ["campaign_id"], unique=False)

    op.create_table(
        "creative_traits",
        sa.Column(
            "creative_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column(
            "hook_type", sa.String(length=64), nullable=True, comment="e.g. problem, question"
        ),
        sa.Column("avatar_type", sa.String(length=64), nullable=True, comment="e.g. woman_25_34"),
        sa.Column(
            "length_bucket", sa.String(length=16), nullable=True, comment="e.g. 0-8s, static"
        ),
        sa.Column(
            "product_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=True
        ),
        sa.Column("voiceover", sa.Boolean(), nullable=True),
        sa.Column("format", sa.String(length=64), nullable=True, comment="e.g. 9x16_ugc_selfie"),
        sa.Column("angle", sa.String(length=128), nullable=True, comment="e.g. saves_time"),
        sa.Column("cta", sa.String(length=64), nullable=True, comment="e.g. shop_now"),
        sa.Column(
            "extra",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["creative_id"],
            ["creatives.id"],
            name=op.f("fk_creative_traits_creative_id_creatives"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_creative_traits_product_id_products"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("creative_id", name=op.f("pk_creative_traits")),
    )
    with op.batch_alter_table("creative_traits", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_creative_traits_product_id"), ["product_id"], unique=False
        )

    op.create_table(
        "generation_jobs",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column(
            "creative_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=True
        ),
        sa.Column("higgsfield_job_id", sa.String(length=128), nullable=True),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column(
            "kind",
            sa.Enum(
                "video",
                "image",
                name="creative_type",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "queued",
                "running",
                "succeeded",
                "failed",
                "cancelled",
                name="generation_status",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "request",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
        sa.Column(
            "result",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
        sa.Column("cost_usd", sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column("retries", sa.Integer(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["creative_id"],
            ["creatives.id"],
            name=op.f("fk_generation_jobs_creative_id_creatives"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_generation_jobs")),
        sa.UniqueConstraint("higgsfield_job_id", name=op.f("uq_generation_jobs_higgsfield_job_id")),
    )
    with op.batch_alter_table("generation_jobs", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_generation_jobs_creative_id"), ["creative_id"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_generation_jobs_status"), ["status"], unique=False)

    op.create_table(
        "ads",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column(
            "ad_set_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column(
            "platform",
            sa.Enum(
                "google",
                "meta",
                "tiktok",
                name="platform",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("external_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=512), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "paused",
                "pending_review",
                "rejected",
                "archived",
                "deleted",
                "unknown",
                name="entity_status",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["ad_set_id"], ["ad_sets.id"], name=op.f("fk_ads_ad_set_id_ad_sets"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ads")),
        sa.UniqueConstraint("platform", "external_id", name=op.f("uq_ads_platform_external_id")),
    )
    with op.batch_alter_table("ads", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_ads_ad_set_id"), ["ad_set_id"], unique=False)

    op.create_table(
        "ad_metrics_daily",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column("ad_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("spend", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("impressions", sa.BigInteger(), nullable=False),
        sa.Column("clicks", sa.BigInteger(), nullable=False),
        sa.Column("video_3s_views", sa.BigInteger(), nullable=False),
        sa.Column("add_to_cart", sa.BigInteger(), nullable=False),
        sa.Column(
            "purchases",
            sa.BigInteger(),
            nullable=False,
            comment="Platform-reported; diagnostics only",
        ),
        sa.Column(
            "platform_revenue",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
            comment="Platform-reported; diagnostics only",
        ),
        sa.Column(
            "synced_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["ad_id"], ["ads.id"], name=op.f("fk_ad_metrics_daily_ad_id_ads"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ad_metrics_daily")),
        sa.UniqueConstraint("ad_id", "date", name=op.f("uq_ad_metrics_daily_ad_id_date")),
    )
    with op.batch_alter_table("ad_metrics_daily", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_ad_metrics_daily_ad_id"), ["ad_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_ad_metrics_daily_date"), ["date"], unique=False)

    op.create_table(
        "creative_ad_links",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column(
            "creative_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("ad_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column(
            "platform",
            sa.Enum(
                "google",
                "meta",
                "tiktok",
                name="platform",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("external_ad_id", sa.String(length=64), nullable=False),
        sa.Column(
            "platform_asset_id",
            sa.String(length=128),
            nullable=True,
            comment="Uploaded video/image id on the platform (YouTube id for Google)",
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["ad_id"], ["ads.id"], name=op.f("fk_creative_ad_links_ad_id_ads"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["creative_id"],
            ["creatives.id"],
            name=op.f("fk_creative_ad_links_creative_id_creatives"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_creative_ad_links")),
        sa.UniqueConstraint(
            "creative_id", "ad_id", name=op.f("uq_creative_ad_links_creative_id_ad_id")
        ),
    )
    with op.batch_alter_table("creative_ad_links", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_creative_ad_links_ad_id"), ["ad_id"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_creative_ad_links_creative_id"), ["creative_id"], unique=False
        )

    op.create_table(
        "orders",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column("shopify_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=True, comment="e.g. #1001"),
        sa.Column(
            "customer_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=True
        ),
        sa.Column("placed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "order_date", sa.Date(), nullable=False, comment="placed_at in the store timezone"
        ),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("financial_status", sa.String(length=32), nullable=True),
        sa.Column("fulfillment_status", sa.String(length=32), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("test", sa.Boolean(), nullable=False),
        sa.Column("source_name", sa.String(length=64), nullable=True),
        sa.Column("is_first_order", sa.Boolean(), nullable=True),
        sa.Column("subtotal_price", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("total_discounts", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("shipping_revenue", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("total_tax", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("total_price", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("total_refunded", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("refunded_tax", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("payment_fees", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("shipping_cost", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("landing_site", sa.Text(), nullable=True),
        sa.Column("referring_site", sa.Text(), nullable=True),
        sa.Column("utm_source", sa.String(length=255), nullable=True),
        sa.Column("utm_medium", sa.String(length=255), nullable=True),
        sa.Column("utm_campaign", sa.String(length=255), nullable=True),
        sa.Column("utm_content", sa.String(length=255), nullable=True),
        sa.Column("utm_term", sa.String(length=255), nullable=True),
        sa.Column("gclid", sa.String(length=255), nullable=True),
        sa.Column("fbclid", sa.String(length=512), nullable=True),
        sa.Column("ttclid", sa.String(length=255), nullable=True),
        sa.Column(
            "attributed_platform",
            sa.Enum(
                "google",
                "meta",
                "tiktok",
                name="platform",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=True,
        ),
        sa.Column(
            "attributed_campaign_id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=True,
        ),
        sa.Column(
            "attributed_ad_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=True
        ),
        sa.Column(
            "attribution_method",
            sa.Enum(
                "click_id",
                "utm",
                "manual",
                "none",
                name="attribution_method",
                native_enum=False,
                create_constraint=True,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "raw",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
        sa.Column("shopify_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["attributed_ad_id"],
            ["ads.id"],
            name=op.f("fk_orders_attributed_ad_id_ads"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["attributed_campaign_id"],
            ["campaigns.id"],
            name=op.f("fk_orders_attributed_campaign_id_campaigns"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
            name=op.f("fk_orders_customer_id_customers"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_orders")),
        sa.UniqueConstraint("shopify_id", name=op.f("uq_orders_shopify_id")),
    )
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_orders_attributed_ad_id"), ["attributed_ad_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_orders_attributed_campaign_id"), ["attributed_campaign_id"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_orders_customer_id"), ["customer_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_orders_fbclid"), ["fbclid"], unique=False)
        batch_op.create_index(batch_op.f("ix_orders_gclid"), ["gclid"], unique=False)
        batch_op.create_index(batch_op.f("ix_orders_order_date"), ["order_date"], unique=False)
        batch_op.create_index(batch_op.f("ix_orders_ttclid"), ["ttclid"], unique=False)

    op.create_table(
        "order_items",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column("order_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column("shopify_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "product_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=True
        ),
        sa.Column(
            "variant_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=True
        ),
        sa.Column("sku", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=512), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(precision=14, scale=2), nullable=False, comment="Unit price"),
        sa.Column("total_discount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("unit_cost", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            name=op.f("fk_order_items_order_id_orders"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_order_items_product_id_products"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["variant_id"],
            ["product_variants.id"],
            name=op.f("fk_order_items_variant_id_product_variants"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_items")),
        sa.UniqueConstraint("shopify_id", name=op.f("uq_order_items_shopify_id")),
    )
    with op.batch_alter_table("order_items", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_order_items_order_id"), ["order_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_order_items_product_id"), ["product_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_order_items_variant_id"), ["variant_id"], unique=False)

    op.create_table(
        "refunds",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column("shopify_id", sa.BigInteger(), nullable=False),
        sa.Column("order_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column("refunded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("tax_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["order_id"], ["orders.id"], name=op.f("fk_refunds_order_id_orders"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_refunds")),
        sa.UniqueConstraint("shopify_id", name=op.f("uq_refunds_shopify_id")),
    )
    with op.batch_alter_table("refunds", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_refunds_order_id"), ["order_id"], unique=False)

    op.execute(V_ORDER_PROFIT)
    op.execute(V_AD_DAILY_PROFIT)
    op.execute(V_CREATIVE_DAILY_PROFIT)

    settings = sa.table(
        "settings",
        sa.column("key", sa.String),
        sa.column("value", sa.JSON().with_variant(postgresql.JSONB(), "postgresql")),
        sa.column("description", sa.Text),
    )
    op.bulk_insert(
        settings, [{"key": k, "value": v, "description": d} for k, v, d in SETTINGS_SEED]
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS v_creative_daily_profit")
    op.execute("DROP VIEW IF EXISTS v_ad_daily_profit")
    op.execute("DROP VIEW IF EXISTS v_order_profit")
    with op.batch_alter_table("refunds", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_refunds_order_id"))

    op.drop_table("refunds")
    with op.batch_alter_table("order_items", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_order_items_variant_id"))
        batch_op.drop_index(batch_op.f("ix_order_items_product_id"))
        batch_op.drop_index(batch_op.f("ix_order_items_order_id"))

    op.drop_table("order_items")
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_orders_ttclid"))
        batch_op.drop_index(batch_op.f("ix_orders_order_date"))
        batch_op.drop_index(batch_op.f("ix_orders_gclid"))
        batch_op.drop_index(batch_op.f("ix_orders_fbclid"))
        batch_op.drop_index(batch_op.f("ix_orders_customer_id"))
        batch_op.drop_index(batch_op.f("ix_orders_attributed_campaign_id"))
        batch_op.drop_index(batch_op.f("ix_orders_attributed_ad_id"))

    op.drop_table("orders")
    with op.batch_alter_table("creative_ad_links", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_creative_ad_links_creative_id"))
        batch_op.drop_index(batch_op.f("ix_creative_ad_links_ad_id"))

    op.drop_table("creative_ad_links")
    with op.batch_alter_table("ad_metrics_daily", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_ad_metrics_daily_date"))
        batch_op.drop_index(batch_op.f("ix_ad_metrics_daily_ad_id"))

    op.drop_table("ad_metrics_daily")
    with op.batch_alter_table("ads", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_ads_ad_set_id"))

    op.drop_table("ads")
    with op.batch_alter_table("generation_jobs", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_generation_jobs_status"))
        batch_op.drop_index(batch_op.f("ix_generation_jobs_creative_id"))

    op.drop_table("generation_jobs")
    with op.batch_alter_table("creative_traits", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_creative_traits_product_id"))

    op.drop_table("creative_traits")
    with op.batch_alter_table("ad_sets", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_ad_sets_campaign_id"))

    op.drop_table("ad_sets")
    with op.batch_alter_table("product_variants", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_product_variants_sku"))
        batch_op.drop_index(batch_op.f("ix_product_variants_product_id"))

    op.drop_table("product_variants")
    with op.batch_alter_table("creatives", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_creatives_product_id"))
        batch_op.drop_index(batch_op.f("ix_creatives_parent_creative_id"))

    op.drop_table("creatives")
    with op.batch_alter_table("campaigns", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_campaigns_ad_account_id"))

    op.drop_table("campaigns")
    with op.batch_alter_table("actions_log", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_actions_log_created_at"))
        batch_op.drop_index(batch_op.f("ix_actions_log_approval_id"))
        batch_op.drop_index(batch_op.f("ix_actions_log_action_type"))

    op.drop_table("actions_log")
    op.drop_table("settings")
    op.drop_table("products")
    with op.batch_alter_table("pending_approvals", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_pending_approvals_status"))

    op.drop_table("pending_approvals")
    with op.batch_alter_table("job_runs", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_job_runs_job_name"))

    op.drop_table("job_runs")
    op.drop_table("customers")
    op.drop_table("ad_accounts")
