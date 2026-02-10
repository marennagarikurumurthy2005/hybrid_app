import logging
from typing import Optional, List
from pymongo import ReturnDocument
from django.conf import settings
from core.db import get_db
from core.utils import utcnow, to_object_id


def get_balance(user_id: str):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return 0
    user_doc = db.users.find_one({"_id": oid})
    return user_doc.get("wallet_balance", 0) if user_doc else 0


def debit_wallet(user_id: str, amount: int, reason: str, source: str, reference: Optional[str] = None):
    if amount <= 0:
        return None
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    user_doc = db.users.find_one_and_update(
        {"_id": oid, "wallet_balance": {"$gte": amount}},
        {"$inc": {"wallet_balance": -amount}},
        return_document=ReturnDocument.AFTER,
    )
    if not user_doc:
        return None
    txn = {
        "user_id": oid,
        "amount": amount,
        "type": "DEBIT",
        "reason": reason,
        "source": source,
        "reference": reference,
        "balance_after": user_doc.get("wallet_balance", 0),
        "created_at": utcnow(),
    }
    result = db.wallet_transactions.insert_one(txn)
    txn["_id"] = result.inserted_id
    try:
        create_ledger_transaction(
            "WALLET",
            str(result.inserted_id),
            [
                {"user_id": user_id, "account": "USER_WALLET", "direction": "DEBIT", "amount": amount},
                {"account": "PLATFORM_CASH", "direction": "CREDIT", "amount": amount},
            ],
            meta={"reason": reason, "source": source, "reference": reference},
        )
    except Exception as exc:
        logger.warning("ledger_debit_failed user_id=%s error=%s", user_id, exc)
    return txn


def credit_wallet(
    user_id: str,
    amount: int,
    reason: str,
    source: str,
    reference: Optional[str] = None,
    is_refund: bool = False,
):
    if amount <= 0:
        return None
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    user_doc = db.users.find_one_and_update(
        {"_id": oid},
        {"$inc": {"wallet_balance": amount}},
        return_document=ReturnDocument.AFTER,
    )
    if not user_doc:
        return None
    txn = {
        "user_id": oid,
        "amount": amount,
        "type": "CREDIT",
        "reason": reason,
        "source": source,
        "reference": reference,
        "is_refund": is_refund,
        "balance_after": user_doc.get("wallet_balance", 0),
        "created_at": utcnow(),
    }
    result = db.wallet_transactions.insert_one(txn)
    txn["_id"] = result.inserted_id
    try:
        create_ledger_transaction(
            "WALLET",
            str(result.inserted_id),
            [
                {"account": "PLATFORM_CASH", "direction": "DEBIT", "amount": amount},
                {"user_id": user_id, "account": "USER_WALLET", "direction": "CREDIT", "amount": amount},
            ],
            meta={"reason": reason, "source": source, "reference": reference, "is_refund": is_refund},
        )
    except Exception as exc:
        logger.warning("ledger_credit_failed user_id=%s error=%s", user_id, exc)
    return txn


def refund_wallet(user_id: str, amount: int, reason: str, source: str, reference: Optional[str] = None):
    return credit_wallet(user_id, amount, reason, source, reference=reference, is_refund=True)


def list_transactions(user_id: str, limit: int = 50):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return []
    return list(db.wallet_transactions.find({"user_id": oid}).sort("created_at", -1).limit(limit))


logger = logging.getLogger(__name__)

LEDGER_ENTRY_COLLECTION = "ledger_entries"
LEDGER_TX_COLLECTION = "ledger_transactions"


def ensure_ledger_indexes():
    db = get_db()
    db[LEDGER_ENTRY_COLLECTION].create_index([("user_id", 1), ("created_at", -1)], name="ledger_entries_user_created")
    db[LEDGER_ENTRY_COLLECTION].create_index([("reference_type", 1), ("reference_id", 1)], name="ledger_entries_reference")
    db[LEDGER_TX_COLLECTION].create_index([("created_at", -1)], name="ledger_tx_created")


def create_ledger_transaction(reference_type: str, reference_id: str, entries: List[dict], meta: Optional[dict] = None):
    ensure_ledger_indexes()
    db = get_db()
    debit_total = sum(int(e.get("amount", 0)) for e in entries if e.get("direction") == "DEBIT")
    credit_total = sum(int(e.get("amount", 0)) for e in entries if e.get("direction") == "CREDIT")
    if debit_total != credit_total:
        raise ValueError("Ledger not balanced")
    tx_doc = {
        "reference_type": reference_type,
        "reference_id": to_object_id(reference_id) if reference_id else None,
        "amount": debit_total,
        "meta": meta or {},
        "created_at": utcnow(),
    }
    result = db[LEDGER_TX_COLLECTION].insert_one(tx_doc)
    tx_doc["_id"] = result.inserted_id
    for entry in entries:
        entry_doc = {
            "transaction_id": tx_doc["_id"],
            "user_id": to_object_id(entry.get("user_id")) if entry.get("user_id") else None,
            "account": entry.get("account"),
            "direction": entry.get("direction"),
            "amount": int(entry.get("amount", 0)),
            "reference_type": reference_type,
            "reference_id": tx_doc.get("reference_id"),
            "created_at": utcnow(),
            "meta": entry.get("meta") or {},
        }
        db[LEDGER_ENTRY_COLLECTION].insert_one(entry_doc)
    return tx_doc


def list_ledger_entries(user_id: str, limit: int = 50):
    ensure_ledger_indexes()
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return []
    cursor = db[LEDGER_ENTRY_COLLECTION].find({"user_id": oid}).sort("created_at", -1).limit(limit)
    return list(cursor)


def _commission_pct():
    return float(getattr(settings, "COMMISSION_PCT", 0.2))


def settle_order(order_id: str):
    ensure_ledger_indexes()
    db = get_db()
    oid = to_object_id(order_id)
    if not oid:
        return None
    order = db.orders.find_one({"_id": oid})
    if not order or order.get("settled"):
        return None
    if not order.get("is_paid") and order.get("payment_mode") != "COD":
        return None
    amount = int(order.get("amount_total") or 0)
    if amount <= 0:
        return None
    commission = int(round(amount * _commission_pct()))
    payout = max(amount - commission, 0)
    entries = [
        {"account": "CUSTOMER_PAYMENTS", "direction": "DEBIT", "amount": amount},
        {"account": "PLATFORM_REVENUE", "direction": "CREDIT", "amount": commission},
        {"account": "RESTAURANT_PAYABLE", "direction": "CREDIT", "amount": payout, "user_id": str(order.get("restaurant_id"))},
    ]
    tx = create_ledger_transaction("ORDER", order_id, entries, meta={"commission_pct": _commission_pct()})
    db.orders.update_one({"_id": oid}, {"$set": {"settled": True, "settled_at": utcnow(), "ledger_tx_id": tx.get("_id")}})
    return tx


def settle_ride(ride_id: str):
    ensure_ledger_indexes()
    db = get_db()
    oid = to_object_id(ride_id)
    if not oid:
        return None
    ride = db.rides.find_one({"_id": oid})
    if not ride or ride.get("settled"):
        return None
    if not ride.get("is_paid") and ride.get("payment_mode") != "COD":
        return None
    amount = int(ride.get("fare") or ride.get("amount_total_before_rewards") or 0)
    if amount <= 0:
        return None
    commission = int(round(amount * _commission_pct()))
    payout = max(amount - commission, 0)
    entries = [
        {"account": "CUSTOMER_PAYMENTS", "direction": "DEBIT", "amount": amount},
        {"account": "PLATFORM_REVENUE", "direction": "CREDIT", "amount": commission},
        {"account": "CAPTAIN_PAYABLE", "direction": "CREDIT", "amount": payout, "user_id": str(ride.get("captain_id"))},
    ]
    tx = create_ledger_transaction("RIDE", ride_id, entries, meta={"commission_pct": _commission_pct()})
    db.rides.update_one({"_id": oid}, {"$set": {"settled": True, "settled_at": utcnow(), "ledger_tx_id": tx.get("_id")}})
    return tx


def run_settlements(limit: int = 50):
    db = get_db()
    settled = []
    orders = db.orders.find({"settled": {"$ne": True}, "status": "DELIVERED"}).limit(limit)
    for order in orders:
        try:
            tx = settle_order(str(order.get("_id")))
            if tx:
                settled.append(tx)
        except Exception as exc:
            logger.warning("order_settlement_failed order_id=%s error=%s", order.get("_id"), exc)
    rides = db.rides.find({"settled": {"$ne": True}, "status": "COMPLETED"}).limit(limit)
    for ride in rides:
        try:
            tx = settle_ride(str(ride.get("_id")))
            if tx:
                settled.append(tx)
        except Exception as exc:
            logger.warning("ride_settlement_failed ride_id=%s error=%s", ride.get("_id"), exc)
    return settled
