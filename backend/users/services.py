import logging
import hashlib
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

SESSION_COLLECTION = "auth_sessions"
ADDRESS_COLLECTION = "user_addresses"
FAVORITES_COLLECTION = "favorites"


def _hash_token(token: str) -> str:
    if not token:
        return ""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def ensure_session_indexes():
    db = get_db()
    db[SESSION_COLLECTION].create_index([("user_id", 1), ("created_at", -1)], name="sessions_user_created")
    db[SESSION_COLLECTION].create_index([("refresh_jti", 1)], unique=True, name="sessions_refresh_jti")
    db[SESSION_COLLECTION].create_index([("device_id", 1)], name="sessions_device_id")


def create_session(
    user_id: str,
    refresh_jti: str,
    refresh_token: str,
    device_id: str = None,
    device_name: str = None,
    user_agent: str = None,
    ip_address: str = None,
):
    ensure_session_indexes()
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    if device_id:
        db[SESSION_COLLECTION].update_many(
            {"user_id": oid, "device_id": device_id, "revoked_at": None},
            {"$set": {"revoked_at": utcnow(), "revoked_reason": "NEW_LOGIN"}},
        )
    doc = {
        "user_id": oid,
        "device_id": device_id,
        "device_name": device_name,
        "user_agent": user_agent,
        "ip_address": ip_address,
        "refresh_jti": refresh_jti,
        "refresh_token_hash": _hash_token(refresh_token),
        "created_at": utcnow(),
        "last_seen": utcnow(),
        "revoked_at": None,
        "revoked_reason": None,
    }
    result = db[SESSION_COLLECTION].insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def rotate_session(refresh_jti: str, new_refresh_jti: str, new_refresh_token: str):
    ensure_session_indexes()
    db = get_db()
    result = db[SESSION_COLLECTION].find_one_and_update(
        {"refresh_jti": refresh_jti, "revoked_at": None},
        {"$set": {
            "refresh_jti": new_refresh_jti,
            "refresh_token_hash": _hash_token(new_refresh_token),
            "last_seen": utcnow(),
        }},
        return_document=ReturnDocument.AFTER,
    )
    return result


def revoke_session(refresh_jti: str, reason: str = "LOGOUT"):
    ensure_session_indexes()
    db = get_db()
    result = db[SESSION_COLLECTION].find_one_and_update(
        {"refresh_jti": refresh_jti, "revoked_at": None},
        {"$set": {"revoked_at": utcnow(), "revoked_reason": reason}},
        return_document=ReturnDocument.AFTER,
    )
    return result


def get_session_by_refresh_jti(refresh_jti: str):
    ensure_session_indexes()
    db = get_db()
    return db[SESSION_COLLECTION].find_one({"refresh_jti": refresh_jti})


def list_sessions(user_id: str, include_revoked: bool = False):
    ensure_session_indexes()
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return []
    query = {"user_id": oid}
    if not include_revoked:
        query["revoked_at"] = None
    cursor = db[SESSION_COLLECTION].find(query).sort("created_at", -1)
    return list(cursor)


def ensure_address_indexes():
    db = get_db()
    db[ADDRESS_COLLECTION].create_index([("user_id", 1), ("created_at", -1)], name="addresses_user_created")
    db[ADDRESS_COLLECTION].create_index([("location", "2dsphere")], name="addresses_location_2dsphere")


def create_user_address(user_id: str, data: dict, location: dict = None):
    ensure_address_indexes()
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    is_default = bool(data.get("is_default", False))
    if is_default:
        db[ADDRESS_COLLECTION].update_many({"user_id": oid}, {"$set": {"is_default": False}})
    doc = {
        "user_id": oid,
        "label": data.get("label"),
        "line1": data.get("line1"),
        "line2": data.get("line2"),
        "city": data.get("city"),
        "state": data.get("state"),
        "postal_code": data.get("postal_code"),
        "landmark": data.get("landmark"),
        "location": location,
        "lat": data.get("lat"),
        "lng": data.get("lng"),
        "is_default": is_default,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    result = db[ADDRESS_COLLECTION].insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def list_user_addresses(user_id: str):
    ensure_address_indexes()
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return []
    return list(db[ADDRESS_COLLECTION].find({"user_id": oid}).sort("created_at", -1))


def update_user_address(user_id: str, address_id: str, data: dict, location: dict = None):
    ensure_address_indexes()
    db = get_db()
    oid = to_object_id(user_id)
    aid = to_object_id(address_id)
    if not oid or not aid:
        return None
    update = {k: v for k, v in data.items() if k not in {"lat", "lng"}}
    if "lat" in data:
        update["lat"] = data.get("lat")
    if "lng" in data:
        update["lng"] = data.get("lng")
    if location is not None or ("lat" in data or "lng" in data):
        update["location"] = location
    if "is_default" in data and data.get("is_default"):
        db[ADDRESS_COLLECTION].update_many({"user_id": oid}, {"$set": {"is_default": False}})
        update["is_default"] = True
    update["updated_at"] = utcnow()
    result = db[ADDRESS_COLLECTION].find_one_and_update(
        {"_id": aid, "user_id": oid},
        {"$set": update},
        return_document=ReturnDocument.AFTER,
    )
    return result


def delete_user_address(user_id: str, address_id: str):
    ensure_address_indexes()
    db = get_db()
    oid = to_object_id(user_id)
    aid = to_object_id(address_id)
    if not oid or not aid:
        return False
    result = db[ADDRESS_COLLECTION].delete_one({"_id": aid, "user_id": oid})
    return result.deleted_count > 0


def ensure_favorite_indexes():
    db = get_db()
    db[FAVORITES_COLLECTION].create_index([("user_id", 1), ("favorite_type", 1)], name="favorites_user_type")
    db[FAVORITES_COLLECTION].create_index([("reference_id", 1)], name="favorites_reference")


def add_favorite(user_id: str, favorite_type: str, reference_id: str):
    ensure_favorite_indexes()
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    doc = {
        "user_id": oid,
        "favorite_type": favorite_type,
        "reference_id": to_object_id(reference_id) or reference_id,
        "created_at": utcnow(),
    }
    db[FAVORITES_COLLECTION].update_one(
        {"user_id": oid, "favorite_type": favorite_type, "reference_id": doc["reference_id"]},
        {"$setOnInsert": doc},
        upsert=True,
    )
    return db[FAVORITES_COLLECTION].find_one(
        {"user_id": oid, "favorite_type": favorite_type, "reference_id": doc["reference_id"]}
    )


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
