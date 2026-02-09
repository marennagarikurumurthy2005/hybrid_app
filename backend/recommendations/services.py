from typing import List, Dict, Optional
from pymongo import ASCENDING

from core.db import get_db
from core.utils import utcnow, to_object_id
from rewards.services import REWARD_POINT_VALUE_PAISE

RECOMMENDATION_TYPES = {"RESTAURANT", "MENU_ITEM"}

_index_ready = False


def ensure_indexes():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.recommendations.create_index(
        [("type", ASCENDING), ("reference_id", ASCENDING)],
        name="recommendations_type_ref",
    )
    db.recommendations.create_index([("created_at", ASCENDING)], name="recommendations_created_at")
    _index_ready = True


def _get_reference(rec_type: str, reference_id: str):
    db = get_db()
    oid = to_object_id(reference_id)
    if not oid:
        return None
    if rec_type == "RESTAURANT":
        return db.restaurants.find_one({"_id": oid, "is_active": True})
    if rec_type == "MENU_ITEM":
        return db.menu_items.find_one({"_id": oid, "is_available": True})
    return None


def create_recommendation(
    created_by: str,
    rec_type: str,
    reference_id: str,
    title: str,
    description: Optional[str],
):
    ensure_indexes()
    rec_type = (rec_type or "").upper()
    if rec_type not in RECOMMENDATION_TYPES:
        raise ValueError("Invalid recommendation type")
    ref_doc = _get_reference(rec_type, reference_id)
    if not ref_doc:
        raise ValueError("Invalid reference id")

    db = get_db()
    doc = {
        "type": rec_type,
        "reference_id": to_object_id(reference_id),
        "title": title,
        "description": description,
        "created_by": to_object_id(created_by),
        "created_at": utcnow(),
    }
    result = db.recommendations.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def list_recommendations(limit: int = 200):
    db = get_db()
    return list(db.recommendations.find().sort("created_at", -1).limit(limit))


def delete_recommendation(recommendation_id: str):
    db = get_db()
    oid = to_object_id(recommendation_id)
    if not oid:
        raise ValueError("Invalid recommendation id")
    result = db.recommendations.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise ValueError("Recommendation not found")
    return True


def list_user_recommendations(limit: int = 200):
    db = get_db()
    recs = list(db.recommendations.find().sort("created_at", -1).limit(limit))
    results = []
    for rec in recs:
        base = {
            "_id": rec.get("_id"),
            "type": rec.get("type"),
            "reference_id": rec.get("reference_id"),
            "title": rec.get("title"),
            "description": rec.get("description"),
            "created_at": rec.get("created_at"),
        }
        if rec.get("type") == "RESTAURANT":
            restaurant = db.restaurants.find_one({"_id": rec.get("reference_id"), "is_active": True})
            if not restaurant:
                continue
            base["restaurant"] = restaurant
        elif rec.get("type") == "MENU_ITEM":
            menu_item = db.menu_items.find_one({"_id": rec.get("reference_id"), "is_available": True})
            if not menu_item:
                continue
            base["menu_item"] = menu_item
            restaurant = None
            if menu_item.get("restaurant_id"):
                restaurant = db.restaurants.find_one({"_id": menu_item.get("restaurant_id")})
            if restaurant:
                base["restaurant"] = restaurant
        results.append(base)
    return results


def calculate_recommendation_points(restaurant_id: str, order_items: List[Dict]):
    if not order_items:
        return 0
    db = get_db()
    rid = to_object_id(restaurant_id)
    if not rid:
        return 0
    restaurant_rec = db.recommendations.find_one({"type": "RESTAURANT", "reference_id": rid})
    if restaurant_rec:
        total_paise = sum(int(item.get("total", 0)) for item in order_items)
        return int(total_paise // REWARD_POINT_VALUE_PAISE)

    item_ids = [item.get("menu_item_id") for item in order_items if item.get("menu_item_id")]
    if not item_ids:
        return 0
    recs = list(db.recommendations.find({"type": "MENU_ITEM", "reference_id": {"$in": item_ids}}))
    if not recs:
        return 0
    rec_ids = {rec.get("reference_id") for rec in recs}
    total_paise = sum(
        int(item.get("total", 0))
        for item in order_items
        if item.get("menu_item_id") in rec_ids
    )
    return int(total_paise // REWARD_POINT_VALUE_PAISE)
