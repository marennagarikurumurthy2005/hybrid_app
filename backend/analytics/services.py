from datetime import datetime
from typing import Dict

from core.db import get_db
from core.utils import to_object_id


def _bucket_key(dt: datetime, period: str):
    if period == "daily":
        return dt.strftime("%Y-%m-%d")
    if period == "weekly":
        year, week, _ = dt.isocalendar()
        return f"{year}-W{week:02d}"
    if period == "monthly":
        return dt.strftime("%Y-%m")
    return dt.strftime("%Y-%m-%d")


def _init_bucket():
    return {"credits": 0, "debits": 0, "rewards": 0, "refunds": 0}


def wallet_analytics(user_id: str):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None

    txns = list(db.wallet_transactions.find({"user_id": oid}).sort("created_at", -1))
    totals = _init_bucket()
    daily: Dict[str, Dict] = {}
    weekly: Dict[str, Dict] = {}
    monthly: Dict[str, Dict] = {}

    for txn in txns:
        amount = int(txn.get("amount", 0))
        ttype = txn.get("type")
        reason = txn.get("reason")
        is_refund = txn.get("is_refund", False)
        created_at = txn.get("created_at")
        if not created_at:
            continue

        if ttype == "CREDIT":
            totals["credits"] += amount
        if ttype == "DEBIT":
            totals["debits"] += amount
        if reason == "FOOD_REWARD":
            totals["rewards"] += amount
        if is_refund:
            totals["refunds"] += amount

        for period, bucket in (("daily", daily), ("weekly", weekly), ("monthly", monthly)):
            key = _bucket_key(created_at, period)
            if key not in bucket:
                bucket[key] = _init_bucket()
            if ttype == "CREDIT":
                bucket[key]["credits"] += amount
            if ttype == "DEBIT":
                bucket[key]["debits"] += amount
            if reason == "FOOD_REWARD":
                bucket[key]["rewards"] += amount
            if is_refund:
                bucket[key]["refunds"] += amount

    return {
        "totals": totals,
        "daily": daily,
        "weekly": weekly,
        "monthly": monthly,
    }
