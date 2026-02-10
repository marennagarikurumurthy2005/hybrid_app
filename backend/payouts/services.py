from typing import Optional
from pymongo import ReturnDocument, ASCENDING

from core.db import get_db
from core.utils import utcnow, to_object_id

_index_ready = False


def ensure_indexes():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.captain_wallet.create_index([("captain_id", ASCENDING)], unique=True, name="captain_wallet_captain")
    db.captain_wallet_txns.create_index([("captain_id", ASCENDING), ("created_at", -1)], name="captain_wallet_txn")
    db.payouts.create_index([("captain_id", ASCENDING), ("created_at", -1)], name="payouts_captain_created")
    db.bank_accounts.create_index([("captain_id", ASCENDING)], unique=True, name="bank_accounts_captain")
    _index_ready = True


def _ensure_wallet(captain_id: str):
    ensure_indexes()
    db = get_db()
    cid = to_object_id(captain_id)
    if not cid:
        return None
    doc = db.captain_wallet.find_one({"captain_id": cid})
    if doc:
        return doc
    db.captain_wallet.insert_one({"captain_id": cid, "balance": 0, "updated_at": utcnow()})
    return db.captain_wallet.find_one({"captain_id": cid})


def get_wallet(captain_id: str):
    return _ensure_wallet(captain_id)


def credit_wallet(captain_id: str, amount: int, reason: str, reference: Optional[str] = None):
    if amount <= 0:
        return None
    ensure_indexes()
    db = get_db()
    cid = to_object_id(captain_id)
    if not cid:
        return None
    wallet = db.captain_wallet.find_one_and_update(
        {"captain_id": cid},
        {"$inc": {"balance": int(amount)}, "$set": {"updated_at": utcnow()}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    txn = {
        "captain_id": cid,
        "amount": int(amount),
        "type": "CREDIT",
        "reason": reason,
        "reference": reference,
        "balance_after": wallet.get("balance", 0),
        "created_at": utcnow(),
    }
    db.captain_wallet_txns.insert_one(txn)
    return txn


def debit_wallet(captain_id: str, amount: int, reason: str, reference: Optional[str] = None):
    if amount <= 0:
        return None
    ensure_indexes()
    db = get_db()
    cid = to_object_id(captain_id)
    if not cid:
        return None
    wallet = db.captain_wallet.find_one_and_update(
        {"captain_id": cid, "balance": {"$gte": int(amount)}},
        {"$inc": {"balance": -int(amount)}, "$set": {"updated_at": utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    if not wallet:
        return None
    txn = {
        "captain_id": cid,
        "amount": int(amount),
        "type": "DEBIT",
        "reason": reason,
        "reference": reference,
        "balance_after": wallet.get("balance", 0),
        "created_at": utcnow(),
    }
    db.captain_wallet_txns.insert_one(txn)
    return txn


def request_payout(captain_id: str, amount: int):
    if amount <= 0:
        raise ValueError("Invalid amount")
    debit = debit_wallet(captain_id, amount, "PAYOUT_REQUEST", reference=None)
    if not debit:
        raise ValueError("Insufficient balance")
    db = get_db()
    tds_amount = int(round(int(amount) * 0.01))
    doc = {
        "captain_id": to_object_id(captain_id),
        "amount": int(amount),
        "tds_amount": tds_amount,
        "net_amount": max(0, int(amount) - tds_amount),
        "status": "PENDING",
        "requested_at": utcnow(),
    }
    db.payouts.insert_one(doc)
    return doc


def list_payouts(captain_id: str, limit: int = 50):
    db = get_db()
    cid = to_object_id(captain_id)
    if not cid:
        return []
    return list(db.payouts.find({"captain_id": cid}).sort("requested_at", -1).limit(limit))


def link_bank_account(captain_id: str, account_number: str, ifsc: str, name: str, upi: Optional[str] = None):
    ensure_indexes()
    db = get_db()
    cid = to_object_id(captain_id)
    if not cid:
        return None
    doc = {
        "captain_id": cid,
        "account_number": account_number,
        "ifsc": ifsc,
        "name": name,
        "upi": upi,
        "updated_at": utcnow(),
    }
    db.bank_accounts.update_one({"captain_id": cid}, {"$set": doc}, upsert=True)
    return db.bank_accounts.find_one({"captain_id": cid})
