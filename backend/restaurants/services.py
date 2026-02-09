from typing import Optional
from core.db import get_db
from core.utils import utcnow, to_object_id
from core.geo_utils import to_point


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


def add_menu_item(restaurant_id: str, name: str, price: int, is_available: bool = True):
    db = get_db()
    doc = {
        "restaurant_id": to_object_id(restaurant_id),
        "name": name,
        "price": int(price),
        "is_available": is_available,
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
