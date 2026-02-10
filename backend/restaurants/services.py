import logging
from typing import Optional, List
from pymongo import ASCENDING, ReturnDocument

from core.db import get_db
from core.utils import utcnow, to_object_id

logger = logging.getLogger(__name__)

RESTAURANT_PROFILE_EDITABLE_FIELDS = {
    "name",
    "logo_url",
    "address",
    "opening_time",
    "closing_time",
    "is_open",
    "support_phone",
}

RESTAURANT_PROFILE_BLOCKED_FIELDS = {
    "_id",
    "owner_id",
    "phone",
    "role",
    "wallet_balance",
    "ratings",
    "average_rating",
    "total_ratings",
    "earnings",
    "is_verified",
    "support_phone_verified",
    "is_active",
    "is_recommended",
    "created_at",
    "updated_at",
    "deleted_at",
}
from core.geo_utils import to_point

_index_ready = False


def ensure_indexes():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.restaurants.create_index([("is_recommended", ASCENDING)], name="restaurants_is_recommended")
    db.menu_items.create_index([("is_recommended", ASCENDING)], name="menu_items_is_recommended")
    _index_ready = True


def create_restaurant(
    owner_id: str,
    name: str,
    address: Optional[str],
    phone: Optional[str],
    lat: Optional[float] = None,
    lng: Optional[float] = None,
):
    db = get_db()
    doc = {
        "owner_id": to_object_id(owner_id),
        "name": name,
        "address": address,
        "phone": phone,
        "location": to_point(lat, lng) if lat is not None and lng is not None else None,
        "is_active": True,
        "is_recommended": False,
        "created_at": utcnow(),
    }
    result = db.restaurants.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def get_restaurant(restaurant_id: str):
    db = get_db()
    oid = to_object_id(restaurant_id)
    if not oid:
        return None
    return db.restaurants.find_one({"_id": oid})


def get_restaurant_by_owner(owner_id: str):
    db = get_db()
    oid = to_object_id(owner_id)
    if not oid:
        return None
    return db.restaurants.find_one({"owner_id": oid})


def add_menu_item(restaurant_id: str, name: str, price: int, is_available: bool = True):
    db = get_db()
    doc = {
        "restaurant_id": to_object_id(restaurant_id),
        "name": name,
        "price": int(price),
        "is_available": is_available,
        "is_recommended": False,
        "created_at": utcnow(),
    }
    result = db.menu_items.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def list_menu_items(restaurant_id: str):
    db = get_db()
    oid = to_object_id(restaurant_id)
    if not oid:
        return []
    return list(db.menu_items.find({"restaurant_id": oid, "is_available": True}))


def set_restaurant_recommended(restaurant_id: str, is_recommended: bool):
    ensure_indexes()
    db = get_db()
    oid = to_object_id(restaurant_id)
    if not oid:
        return None
    db.restaurants.update_one({"_id": oid}, {"$set": {"is_recommended": bool(is_recommended)}})
    return db.restaurants.find_one({"_id": oid})


def set_menu_item_recommended(menu_item_id: str, is_recommended: bool):
    ensure_indexes()
    db = get_db()
    oid = to_object_id(menu_item_id)
    if not oid:
        return None
    db.menu_items.update_one({"_id": oid}, {"$set": {"is_recommended": bool(is_recommended)}})
    return db.menu_items.find_one({"_id": oid})


def list_recommended_restaurants(limit: int = 50):
    ensure_indexes()
    db = get_db()
    cursor = db.restaurants.find({"is_active": True, "is_recommended": True}).limit(limit)
    return list(cursor)


def list_recommended_menu_items(limit: int = 50):
    ensure_indexes()
    db = get_db()
    cursor = db.menu_items.find({"is_available": True, "is_recommended": True}).limit(limit)
    return list(cursor)


def update_restaurant_profile(owner_id: str, updates: dict):
    if not updates:
        return None
    db = get_db()
    oid = to_object_id(owner_id)
    if not oid:
        return None
    updated = db.restaurants.find_one_and_update(
        {"owner_id": oid},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    if updated:
        logger.info("restaurant_profile_updated owner_id=%s fields=%s", owner_id, sorted(updates.keys()))
    return updated
