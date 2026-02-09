import numpy as np
from sklearn.ensemble import IsolationForest
from pymongo import ASCENDING

from core.db import get_db
from core.utils import utcnow
from rides.services import haversine_km

_index_ready = False


def ensure_indexes():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.fraud_flags.create_index([("user_id", ASCENDING)], name="fraud_user")
    db.fraud_flags.create_index([("created_at", ASCENDING)], name="fraud_created_at")
    _index_ready = True


def _wallet_stats(user_id):
    db = get_db()
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$type",
            "amount": {"$sum": "$amount"},
            "count": {"$sum": 1},
        }},
    ]
    results = list(db.wallet_transactions.aggregate(pipeline))
    stats = {item["_id"]: item for item in results}
    credit = stats.get("CREDIT", {}).get("amount", 0)
    debit = stats.get("DEBIT", {}).get("amount", 0)

    reward_sum = db.wallet_transactions.aggregate([
        {"$match": {"user_id": user_id, "reason": "FOOD_REWARD"}},
        {"$group": {"_id": None, "amount": {"$sum": "$amount"}, "count": {"$sum": 1}}},
    ])
    reward_doc = next(reward_sum, None)

    refund_sum = db.wallet_transactions.aggregate([
        {"$match": {"user_id": user_id, "is_refund": True}},
        {"$group": {"_id": None, "amount": {"$sum": "$amount"}, "count": {"$sum": 1}}},
    ])
    refund_doc = next(refund_sum, None)

    return {
        "wallet_credit": credit,
        "wallet_debit": debit,
        "reward_amount": (reward_doc or {}).get("amount", 0),
        "reward_count": (reward_doc or {}).get("count", 0),
        "refund_amount": (refund_doc or {}).get("amount", 0),
        "refund_count": (refund_doc or {}).get("count", 0),
    }


def _ride_stats(user_id):
    db = get_db()
    rides = list(db.rides.find({"user_id": user_id}))
    ride_count = 0
    short_rides = 0
    for ride in rides:
        if ride.get("status") == "COMPLETED":
            ride_count += 1
        pickup = ride.get("pickup") or {}
        dropoff = ride.get("dropoff") or {}
        if "lat" in pickup and "lng" in pickup and "lat" in dropoff and "lng" in dropoff:
            distance = haversine_km(pickup["lat"], pickup["lng"], dropoff["lat"], dropoff["lng"])
            if distance < 0.5:
                short_rides += 1
    return {"ride_count": ride_count, "short_rides": short_rides}


def _order_stats(user_id):
    db = get_db()
    order_count = db.orders.count_documents({"user_id": user_id, "status": "DELIVERED"})
    return {"order_count": order_count}


def scan_users(limit: int = 200):
    ensure_indexes()
    db = get_db()
    users = list(db.users.find({"is_active": True}).limit(limit))
    if not users:
        return []

    features = []
    rows = []
    for user in users:
        uid = user.get("_id")
        w = _wallet_stats(uid)
        r = _ride_stats(uid)
        o = _order_stats(uid)
        row = {
            "user_id": uid,
            "wallet_credit": w["wallet_credit"],
            "wallet_debit": w["wallet_debit"],
            "reward_amount": w["reward_amount"],
            "reward_count": w["reward_count"],
            "refund_amount": w["refund_amount"],
            "refund_count": w["refund_count"],
            "ride_count": r["ride_count"],
            "short_rides": r["short_rides"],
            "order_count": o["order_count"],
        }
        rows.append(row)
        features.append([
            row["wallet_credit"],
            row["wallet_debit"],
            row["reward_amount"],
            row["reward_count"],
            row["refund_amount"],
            row["refund_count"],
            row["ride_count"],
            row["short_rides"],
            row["order_count"],
        ])

    if len(features) < 5:
        return []

    model = IsolationForest(n_estimators=200, contamination=0.08, random_state=42)
    preds = model.fit_predict(np.array(features))
    scores = model.decision_function(np.array(features))

    suspicious = []
    for idx, pred in enumerate(preds):
        if pred == -1:
            row = rows[idx]
            score = float(scores[idx])
            flag_doc = {
                "user_id": row["user_id"],
                "score": score,
                "features": row,
                "created_at": utcnow(),
            }
            db.fraud_flags.insert_one(flag_doc)
            suspicious.append(flag_doc)

    return suspicious
