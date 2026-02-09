from typing import Optional
from pymongo import ReturnDocument
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
    db.wallet_transactions.insert_one(txn)
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
    db.wallet_transactions.insert_one(txn)
    return txn


def refund_wallet(user_id: str, amount: int, reason: str, source: str, reference: Optional[str] = None):
    return credit_wallet(user_id, amount, reason, source, reference=reference, is_refund=True)


def list_transactions(user_id: str, limit: int = 50):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return []
    return list(db.wallet_transactions.find({"user_id": oid}).sort("created_at", -1).limit(limit))
