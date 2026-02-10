from typing import Optional
from pymongo import ASCENDING

from core.db import get_db
from core.utils import utcnow, to_object_id

_index_ready = False


def ensure_indexes():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.restaurant_stats.create_index([("restaurant_id", ASCENDING)], name="restaurant_stats_restaurant")
    db.restaurant_orders.create_index([("order_id", ASCENDING)], unique=True, name="restaurant_orders_order")
    db.inventory.create_index([("menu_item_id", ASCENDING)], unique=True, name="inventory_menu_item")
    _index_ready = True


def update_order_status(order_id: str, status: str, prep_time_min: Optional[int] = None):
    db = get_db()
    oid = to_object_id(order_id)
    if not oid:
        return None
    update = {"status": status, "updated_at": utcnow()}
    if prep_time_min is not None:
        update["prep_time_min"] = int(prep_time_min)
    db.orders.update_one({"_id": oid}, {"$set": update})
    db.restaurant_orders.update_one(
        {"order_id": oid},
        {"$set": {"order_id": oid, "status": status, "prep_time_min": prep_time_min, "updated_at": utcnow()}},
        upsert=True,
    )
    return db.orders.find_one({"_id": oid})


def toggle_menu_item(menu_item_id: str, is_available: bool):
    db = get_db()
    oid = to_object_id(menu_item_id)
    if not oid:
        return None
    db.menu_items.update_one({"_id": oid}, {"$set": {"is_available": bool(is_available)}})
    db.inventory.update_one(
        {"menu_item_id": oid},
        {"$set": {"menu_item_id": oid, "is_available": bool(is_available), "updated_at": utcnow()}},
        upsert=True,
    )
    return db.menu_items.find_one({"_id": oid})


def get_analytics(restaurant_id: str):
    db = get_db()
    rid = to_object_id(restaurant_id)
    if not rid:
        return None
    total_orders = db.orders.count_documents({"restaurant_id": rid})
    delivered = db.orders.count_documents({"restaurant_id": rid, "status": "DELIVERED"})
    revenue = 0
    pipeline = [
        {"$match": {"restaurant_id": rid, "is_paid": True}},
        {"$group": {"_id": None, "amount": {"$sum": "$payment_amount"}}},
    ]
    doc = next(db.orders.aggregate(pipeline), None)
    if doc:
        revenue = int(doc.get("amount", 0))
    return {
        "restaurant_id": str(rid),
        "total_orders": total_orders,
        "delivered_orders": delivered,
        "revenue": revenue,
    }
