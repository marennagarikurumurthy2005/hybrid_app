from typing import Optional
from pymongo import ReturnDocument, ASCENDING

from core.db import get_db
from core.utils import utcnow, to_object_id

REWARD_POINT_VALUE_PAISE = 100
REWARD_SOURCE_RECOMMENDATION = "RECOMMENDATION"

_index_ready = False


def ensure_indexes():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.user_rewards.create_index(
        [("user_id", ASCENDING), ("used", ASCENDING), ("created_at", ASCENDING)],
        name="user_rewards_user_used_created",
    )
    _index_ready = True


def get_reward_balance(user_id: str) -> int:
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return 0
    user_doc = db.users.find_one({"_id": oid})
    return int(user_doc.get("reward_balance", 0)) if user_doc else 0


def calculate_redeemable_points(user_id: str, total_amount_paise: int, requested_points: Optional[int]):
    requested = int(requested_points or 0)
    if requested <= 0:
        return 0, 0, get_reward_balance(user_id)
    available = get_reward_balance(user_id)
    if requested > available:
        raise ValueError("Insufficient reward points")
    max_points = int(total_amount_paise) // REWARD_POINT_VALUE_PAISE
    points_to_redeem = min(requested, max_points)
    redeem_amount = points_to_redeem * REWARD_POINT_VALUE_PAISE
    return points_to_redeem, redeem_amount, available


def credit_reward_points(user_id: str, points: int, source: str, related_order: Optional[str] = None):
    if points <= 0:
        return None
    ensure_indexes()
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    user_doc = db.users.find_one_and_update(
        {"_id": oid},
        {"$inc": {"reward_balance": int(points)}},
        return_document=ReturnDocument.AFTER,
    )
    if not user_doc:
        return None
    doc = {
        "user_id": oid,
        "points": int(points),
        "type": "REWARD",
        "source": source,
        "used": False,
        "related_order": to_object_id(related_order) if related_order else None,
        "created_at": utcnow(),
    }
    result = db.user_rewards.insert_one(doc)
    doc["_id"] = result.inserted_id
    doc["balance_after"] = user_doc.get("reward_balance", 0)
    return doc


def redeem_reward_points(user_id: str, points: int, related_order: Optional[str] = None):
    if points <= 0:
        return None
    ensure_indexes()
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    user_doc = db.users.find_one_and_update(
        {"_id": oid, "reward_balance": {"$gte": int(points)}},
        {"$inc": {"reward_balance": -int(points)}},
        return_document=ReturnDocument.AFTER,
    )
    if not user_doc:
        return None

    remaining = int(points)
    rewards = list(db.user_rewards.find({
        "user_id": oid,
        "used": False,
        "points": {"$gt": 0},
    }).sort("created_at", 1))

    for reward in rewards:
        if remaining <= 0:
            break
        reward_points = int(reward.get("points", 0))
        if reward_points <= 0:
            continue
        if reward_points <= remaining:
            db.user_rewards.update_one(
                {"_id": reward["_id"]},
                {"$set": {"used": True, "points": 0}},
            )
            remaining -= reward_points
        else:
            db.user_rewards.update_one(
                {"_id": reward["_id"]},
                {"$set": {"points": reward_points - remaining}},
            )
            remaining = 0

    return {
        "points_redeemed": int(points),
        "balance_after": user_doc.get("reward_balance", 0),
        "related_order": related_order,
    }
