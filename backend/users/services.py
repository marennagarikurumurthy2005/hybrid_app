import logging
from pymongo import ReturnDocument

from core.db import get_db
from core.utils import utcnow, to_object_id

logger = logging.getLogger(__name__)

USER_PROFILE_EDITABLE_FIELDS = {
    "name",
    "email",
    "avatar_url",
    "default_address",
    "preferences",
}

USER_PROFILE_BLOCKED_FIELDS = {
    "_id",
    "phone",
    "role",
    "wallet_balance",
    "reward_points",
    "reward_balance",
    "ratings",
    "average_rating",
    "total_ratings",
    "earnings",
    "is_verified",
    "is_active",
    "fcm_token",
    "created_at",
    "updated_at",
    "deleted_at",
}


def get_user_by_phone(phone: str):
    db = get_db()
    return db.users.find_one({"phone": phone})


def get_user_by_id(user_id: str):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    return db.users.find_one({"_id": oid})


def create_user(phone: str, role: str):
    db = get_db()
    doc = {
        "phone": phone,
        "role": role,
        "wallet_balance": 0,
        "reward_points": 0,
        "reward_balance": 0,
        "is_active": True,
        "created_at": utcnow(),
        "fcm_token": None,
    }
    result = db.users.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def set_fcm_token(user_id: str, fcm_token: str):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    db.users.update_one({"_id": oid}, {"$set": {"fcm_token": fcm_token}})
    return db.users.find_one({"_id": oid})


def update_role(user_id: str, role: str):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    db.users.update_one({"_id": oid}, {"$set": {"role": role}})
    return db.users.find_one({"_id": oid})


def update_user_profile(user_id: str, updates: dict):
    if not updates:
        return None
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    updated = db.users.find_one_and_update(
        {"_id": oid},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    if updated:
        logger.info("user_profile_updated user_id=%s fields=%s", user_id, sorted(updates.keys()))
    return updated
