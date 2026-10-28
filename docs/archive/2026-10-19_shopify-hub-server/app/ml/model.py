"""Creative profit model: LightGBM predicting contribution profit per 1,000 spend from traits.

Gated so it can't mislead early on:
* trains only with >= ``MIN_LABELED`` labeled creatives (lifetime spend >= ``MIN_LABEL_SPEND``);
* is activated only if spend-weighted 5-fold CV error beats the "predict the average"
  baseline by >= ``MIN_IMPROVEMENT``. Otherwise the version is stored as ``inactive`` with the
  reason, and predictions are not offered.

Features: one-hot creative traits (hook_type, avatar_type, angle, length_bucket, format, cta,
voiceover, kind) with a vocabulary learned at training time (rare values -> ``other``),
plus duration and the creative's spend mix across platforms. Samples are weighted by
sqrt(spend): a creative that spent 5,000 is more certain than one that spent 100.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import numpy as np
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.actions import SessionFactory
from app.db import session_scope
from app.log import get_logger
from app.ml.creative_metrics import latest_lifetime
from app.models import Creative, CreativeTrait, MLModel

log = get_logger(__name__)
KIND = "creative_profit_lgbm"
MIN_LABELED = 50
MIN_LABEL_SPEND = Decimal("100")
MIN_IMPROVEMENT = 0.05
MIN_CATEGORY_COUNT = 2
CATEGORICAL = (
    "hook_type",
    "avatar_type",
    "angle",
    "length_bucket",
    "format",
    "cta",
    "voiceover",
    "kind",
)
PLATFORMS = ("google", "meta", "tiktok")
PARAMS = {
    "objective": "regression",
    "learning_rate": 0.05,
    "num_leaves": 15,
    "min_data_in_leaf": 5,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 1,
    "lambda_l2": 1.0,
    "verbose": -1,
    "seed": 7,
    "deterministic": True,
}
ROUNDS = 200


def _value(v: Any) -> str:
    if v is None:
        return "unknown"
    return str(v).lower() if isinstance(v, bool) else str(v)


@dataclass
class Encoder:
    vocab: dict[str, list[str]]

    @classmethod
    def fit(cls, rows: list[dict[str, Any]]) -> Encoder:
        vocab = {}
        for col in CATEGORICAL:
            counts: dict[str, int] = {}
            for r in rows:
                counts[_value(r.get(col))] = counts.get(_value(r.get(col)), 0) + 1
            vocab[col] = [*sorted(v for v, n in counts.items() if n >= MIN_CATEGORY_COUNT), "other"]
        return cls(vocab)

    @property
    def names(self) -> list[str]:
        return (
            [f"{c}={v}" for c in CATEGORICAL for v in self.vocab[c]]
            + ["duration_seconds"]
            + [f"spend_share_{p}" for p in PLATFORMS]
        )

    def row(self, r: dict[str, Any]) -> list[float]:
        out: list[float] = []
        for col in CATEGORICAL:
            v = _value(r.get(col))
            v = v if v in self.vocab[col] else "other"
            out += [1.0 if v == x else 0.0 for x in self.vocab[col]]
        out.append(float(r.get("duration_seconds") or 0))
        shares = r.get("spend_shares") or {}
        out += [float(shares.get(p, 0)) for p in PLATFORMS]
        return out

    def matrix(self, rows: list[dict[str, Any]]) -> np.ndarray:
        return np.array([self.row(r) for r in rows], dtype=float)


def feature_rows(session: Session) -> list[dict[str, Any]]:
    """One row per creative with a lifetime snapshot: traits + label + weight."""
    labels = {m.creative_id: m for m in latest_lifetime(session)}
    if not labels:
        return []
    traits = {
        t.creative_id: t
        for t in session.scalars(
            select(CreativeTrait).where(CreativeTrait.creative_id.in_(list(labels)))
        )
    }
    creatives = {
        c.id: c for c in session.scalars(select(Creative).where(Creative.id.in_(list(labels))))
    }
    shares: dict[int, dict[str, float]] = {}
    for cid, platform, spend in session.execute(
        text("""
        SELECT l.creative_id, a.platform, SUM(m.spend) FROM creative_ad_links l
        JOIN ads a ON a.id = l.ad_id JOIN ad_metrics_daily m ON m.ad_id = a.id
        GROUP BY l.creative_id, a.platform""")
    ):
        shares.setdefault(int(cid), {})[str(platform)] = float(spend or 0)
    rows = []
    for cid, m in labels.items():
        t, c = traits.get(cid), creatives.get(cid)
        if t is None or c is None:
            continue
        total = sum(shares.get(cid, {}).values()) or 1.0
        rows.append(
            {
                "creative_id": cid,
                "kind": c.type.value,
                "duration_seconds": float(c.duration_seconds or 0),
                **{k: getattr(t, k) for k in CATEGORICAL if k != "kind"},
                "spend_shares": {p: v / total for p, v in shares.get(cid, {}).items()},
                "label": float(m.profit_per_1000) if m.profit_per_1000 is not None else None,
                "spend": float(m.spend),
                "labeled": m.spend >= MIN_LABEL_SPEND and m.profit_per_1000 is not None,
            }
        )
    return rows


def _cv(x: np.ndarray, y: np.ndarray, w: np.ndarray, folds: int = 5) -> tuple[float, float]:
    """Spend-weighted RMSE of the model and of the weighted-mean baseline, out of fold."""
    import lightgbm as lgb

    idx = np.random.default_rng(7).permutation(len(y))
    model_err, base_err = [], []
    for k in range(folds):
        test = idx[k::folds]
        train = np.setdiff1d(idx, test)
        booster = lgb.train(
            PARAMS, lgb.Dataset(x[train], y[train], weight=w[train]), num_boost_round=ROUNDS
        )
        pred = booster.predict(x[test])
        base = np.average(y[train], weights=w[train])
        model_err.append(np.average((pred - y[test]) ** 2, weights=w[test]))
        base_err.append(np.average((base - y[test]) ** 2, weights=w[test]))
    return float(np.sqrt(np.mean(model_err))), float(np.sqrt(np.mean(base_err)))


def train(
    *, session_factory: SessionFactory = session_scope, store: Any | None = None
) -> dict[str, Any]:
    """Train a new version; activate it only if it clears the gates. Always records the attempt."""
    import lightgbm as lgb

    with session_factory() as s:
        rows = [r for r in feature_rows(s) if r["labeled"]]
    n = len(rows)

    def save(status: str, notes: str, **kw: Any) -> dict[str, Any]:
        with session_factory() as s:
            if status == "active":
                for old in s.scalars(
                    select(MLModel).where(MLModel.kind == KIND, MLModel.status == "active")
                ):
                    old.status = "retired"
            row = MLModel(kind=KIND, status=status, n_labeled=n, notes=notes, **kw)
            s.add(row)
            s.flush()
            return {
                "model_id": row.id,
                "status": status,
                "n_labeled": n,
                "notes": notes,
                "metrics": kw.get("metrics"),
            }

    if n < MIN_LABELED:
        return save(
            "inactive",
            f"waiting for data: {n}/{MIN_LABELED} creatives with >= {MIN_LABEL_SPEND} lifetime spend",
        )
    enc = Encoder.fit(rows)
    x, y = enc.matrix(rows), np.array([r["label"] for r in rows])
    w = np.sqrt(np.array([r["spend"] for r in rows]))
    rmse, base = _cv(x, y, w)
    improvement = 1 - rmse / base if base else 0.0
    metrics = {
        "cv_rmse": round(rmse, 2),
        "baseline_rmse": round(base, 2),
        "improvement": round(improvement, 4),
        "label_mean": round(float(np.average(y, weights=w)), 2),
    }
    if improvement < MIN_IMPROVEMENT:
        return save(
            "inactive",
            f"not better than predicting the average (improvement {improvement:.1%} < "
            f"{MIN_IMPROVEMENT:.0%}); traits don't explain profit yet",
            metrics=metrics,
            features={"vocab": enc.vocab},
        )
    booster = lgb.train(
        PARAMS, lgb.Dataset(x, y, weight=w, feature_name=_safe(enc.names)), num_boost_round=ROUNDS
    )
    gain = booster.feature_importance(importance_type="gain")
    top = sorted(zip(enc.names, gain, strict=True), key=lambda t: -t[1])[:15]
    metrics["top_features"] = [{"feature": f, "gain": round(float(g), 1)} for f, g in top if g > 0]
    if store is None:
        from app.storage import get_store

        store = get_store()
    key = f"ml/{KIND}/{datetime.now(UTC):%Y%m%dT%H%M%S}.txt"
    store.put(key, booster.model_to_string().encode(), "text/plain")
    _cache.clear()
    return save(
        "active",
        f"trained on {n} creatives; CV error {improvement:.0%} better than baseline",
        metrics=metrics,
        features={"vocab": enc.vocab},
        storage_key=key,
    )


def _safe(names: list[str]) -> list[str]:
    """LightGBM feature names can't contain JSON-special characters."""
    return [
        n.replace("=", "__").replace(":", "_").replace(" ", "_").replace('"', "") for n in names
    ]


_cache: dict[int, tuple[Any, Encoder]] = {}


def active(session: Session) -> MLModel | None:
    return session.scalars(
        select(MLModel)
        .where(MLModel.kind == KIND, MLModel.status == "active")
        .order_by(MLModel.id.desc())
        .limit(1)
    ).first()


def predict(
    trait_rows: list[dict[str, Any]],
    *,
    session_factory: SessionFactory = session_scope,
    store: Any | None = None,
) -> list[float] | None:
    """Predicted profit per 1,000 spend for trait dicts, or None if no model is active."""
    import lightgbm as lgb

    with session_factory() as s:
        m = active(s)
        if m is None or not m.storage_key:
            return None
        model_id, key, vocab = m.id, m.storage_key, (m.features or {}).get("vocab")
    if model_id not in _cache:
        if store is None:
            from app.storage import get_store

            store = get_store()
        _cache.clear()
        _cache[model_id] = (lgb.Booster(model_str=store.get_bytes(key).decode()), Encoder(vocab))
    booster, enc = _cache[model_id]
    return [round(float(p), 2) for p in booster.predict(enc.matrix(trait_rows))]


def status(session: Session) -> dict[str, Any]:
    rows = feature_rows(session)
    labeled = sum(1 for r in rows if r["labeled"])
    m = active(session)
    last = session.scalars(
        select(MLModel).where(MLModel.kind == KIND).order_by(MLModel.id.desc()).limit(1)
    ).first()
    return {
        "model": KIND,
        "target": "contribution profit per 1,000 spend (Shopify orders)",
        "labeled_creatives": labeled,
        "needed": MIN_LABELED,
        "active": bool(m),
        "active_model": {"id": m.id, "trained_at": m.created_at.isoformat(), "metrics": m.metrics}
        if m
        else None,
        "last_attempt": {
            "id": last.id,
            "status": last.status,
            "notes": last.notes,
            "metrics": last.metrics,
            "at": last.created_at.isoformat(),
        }
        if last
        else None,
    }
