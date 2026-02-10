from pymongo import ASCENDING

from core.utils import to_object_id, utcnow
from core.db import get_db

_index_ready = False


def ensure_indexes():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.users.create_index([("created_at", ASCENDING)], name="users_created_at")
    db.captains.create_index([("created_at", ASCENDING)], name="captains_created_at")
    _index_ready = True


def _sum(collection, match: dict, field: str):
    db = get_db()
    pipeline = [
        {"$match": match},
        {"$group": {"_id": None, "amount": {"$sum": f"${field}"}}},
    ]
    doc = next(collection.aggregate(pipeline), None)
    return int(doc["amount"]) if doc and doc.get("amount") is not None else 0


def overview():
    ensure_indexes()
    db = get_db()
    total_users = db.users.count_documents({})
    active_captains = db.captains.count_documents({"is_online": True})

    order_revenue = _sum(db.orders, {"is_paid": True}, "payment_amount")
    ride_revenue = _sum(db.rides, {"is_paid": True}, "payment_amount")
    surge_orders = _sum(db.orders, {"surge_amount": {"$exists": True}}, "surge_amount")
    surge_rides = _sum(db.rides, {"surge_amount": {"$exists": True}}, "surge_amount")

    wallet_total = _sum(db.users, {}, "wallet_balance")

    return {
        "total_users": total_users,
        "active_captains": active_captains,
        "revenue": order_revenue + ride_revenue,
        "surge_impact": surge_orders + surge_rides,
        "wallet_balances": wallet_total,
    }


def list_users(limit: int = 50, skip: int = 0):
    db = get_db()
    cursor = db.users.find({}).skip(skip).limit(limit)
    return list(cursor)


def list_captains(limit: int = 50, skip: int = 0):
    db = get_db()
    cursor = db.captains.find({}).skip(skip).limit(limit)
    return list(cursor)


def verify_captain(captain_id: str, is_verified: bool, reason: str = None):
    db = get_db()
    oid = to_object_id(captain_id)
    if not oid:
        return None
    update = {
        "is_verified": bool(is_verified),
        "verified_at": utcnow() if is_verified else None,
    }
    if reason is not None:
        update["verification_reason"] = reason
    if not is_verified:
        update["is_online"] = False
    result = db.captains.update_one({"user_id": oid}, {"$set": update})
    if result.matched_count == 0:
        result = db.captains.update_one({"_id": oid}, {"$set": update})
        if result.matched_count == 0:
            return None
        return db.captains.find_one({"_id": oid})
    return db.captains.find_one({"user_id": oid})
