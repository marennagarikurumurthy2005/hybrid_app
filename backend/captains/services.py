from core.db import get_db
from core.utils import utcnow, to_object_id
from core.geo_utils import to_point
from notifications import services as notification_services


def ensure_captain_profile(user_id: str):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    existing = db.captains.find_one({"user_id": oid})
    if existing:
        return existing
    doc = {
        "user_id": oid,
        "is_online": False,
        "is_busy": False,
        "location": None,
        "current_job_id": None,
        "current_job_type": None,
        "current_job": None,
        "batched_order_ids": [],
        "average_rating": 5.0,
        "total_ratings": 0,
        "total_trips": 0,
        "cancellations": 0,
        "last_assigned_at": None,
        "last_seen": utcnow(),
        "created_at": utcnow(),
    }
    result = db.captains.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def set_online_status(user_id: str, is_online: bool):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    update = {"is_online": is_online, "last_seen": utcnow()}
    if not is_online:
        update["is_busy"] = False
        update["current_job_id"] = None
        update["current_job_type"] = None
        update["current_job"] = None
    db.captains.update_one({"user_id": oid}, {"$set": update})
    return db.captains.find_one({"user_id": oid})


def update_location(user_id: str, lat: float, lng: float):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    db.captains.update_one(
        {"user_id": oid},
        {"$set": {"location": to_point(lat, lng), "last_seen": utcnow()}},
    )
    updated = db.captains.find_one({"user_id": oid})
    if updated and updated.get("current_job_type"):
        from core import matching_service
        if updated.get("current_job_type") == "ORDER":
            batched = updated.get("batched_order_ids") or []
            if not batched and updated.get("current_job_id"):
                batched = [updated.get("current_job_id")]
            for order_id in batched:
                matching_service.broadcast_location(
                    "ORDER",
                    str(order_id),
                    str(updated.get("user_id")),
                    lat,
                    lng,
                )
        else:
            if updated.get("current_job_id"):
                matching_service.broadcast_location(
                    updated.get("current_job_type"),
                    str(updated.get("current_job_id")),
                    str(updated.get("user_id")),
                    lat,
                    lng,
                )
    return updated


def assign_captain_stub(job_type: str, job_id: str):
    db = get_db()
    pipeline = [
        {
            "$match": {
                "is_online": True,
                "is_busy": False,
                "$or": [
                    {"current_job_id": None},
                    {"current_job_id": {"$exists": False}},
                ],
            }
        },
        {"$sample": {"size": 1}},
    ]
    candidates = list(db.captains.aggregate(pipeline))
    if not candidates:
        return None
    captain = candidates[0]
    db.captains.update_one(
        {"_id": captain["_id"]},
        {"$set": {
            "current_job": {"type": job_type, "id": job_id},
            "current_job_id": to_object_id(job_id),
            "current_job_type": job_type,
            "is_busy": True,
            "last_assigned_at": utcnow(),
        }},
    )
    return captain


def accept_job(user_id: str, job_type: str, job_id: str):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    db.captains.update_one(
        {"user_id": oid},
        {"$set": {
            "current_job": {"type": job_type, "id": job_id},
            "current_job_id": to_object_id(job_id),
            "current_job_type": job_type,
            "is_busy": True,
            "last_assigned_at": utcnow(),
        }},
    )
    if job_type == "ORDER":
        order_oid = to_object_id(job_id)
        order_doc = db.orders.find_one({"_id": order_oid}) if order_oid else None
        db.orders.update_one(
            {"_id": order_oid},
            {"$set": {"status": "ASSIGNED", "captain_id": oid}},
        )
        if order_doc and order_doc.get("user_id"):
            notification_services.send_to_user(
                str(order_doc.get("user_id")),
                "Captain assigned",
                "Your order is on the way.",
                {"order_id": job_id},
            )
    if job_type == "RIDE":
        ride_oid = to_object_id(job_id)
        ride_doc = db.rides.find_one({"_id": ride_oid}) if ride_oid else None
        db.rides.update_one(
            {"_id": ride_oid},
            {"$set": {"status": "ASSIGNED", "captain_id": oid}},
        )
        if ride_doc and ride_doc.get("user_id"):
            notification_services.send_to_user(
                str(ride_doc.get("user_id")),
                "Captain assigned",
                "Your ride has been assigned.",
                {"ride_id": job_id},
            )
    return db.captains.find_one({"user_id": oid})


def complete_job(user_id: str, job_type: str, job_id: str):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    db.captains.update_one(
        {"user_id": oid},
        {"$set": {
            "current_job": None,
            "current_job_id": None,
            "current_job_type": None,
            "is_busy": False,
        }},
    )
    if job_type == "ORDER":
        order_oid = to_object_id(job_id)
        order_doc = db.orders.find_one({"_id": order_oid}) if order_oid else None
        db.orders.update_one(
            {"_id": order_oid},
            {"$set": {"status": "DELIVERED"}},
        )
        db.captains.update_one(
            {"user_id": oid},
            {"$pull": {"batched_order_ids": order_oid}},
        )
        captain_doc = db.captains.find_one({"user_id": oid})
        remaining = captain_doc.get("batched_order_ids") if captain_doc else []
        if remaining:
            db.captains.update_one(
                {"user_id": oid},
                {"$set": {"is_busy": True, "current_job_id": remaining[0], "current_job_type": "ORDER", "current_job": {"type": "ORDER", "id": str(remaining[0])}}},
            )
        from orders import services as order_services
        order_services.award_food_points(job_id)
        if order_doc and order_doc.get("user_id"):
            notification_services.send_to_user(
                str(order_doc.get("user_id")),
                "Order delivered",
                "Your order has been delivered.",
                {"order_id": job_id},
            )
    if job_type == "RIDE":
        ride_oid = to_object_id(job_id)
        ride_doc = db.rides.find_one({"_id": ride_oid}) if ride_oid else None
        db.rides.update_one(
            {"_id": ride_oid},
            {"$set": {"status": "COMPLETED"}},
        )
        if ride_doc and ride_doc.get("user_id"):
            notification_services.send_to_user(
                str(ride_doc.get("user_id")),
                "Ride completed",
                "Your ride is complete.",
                {"ride_id": job_id},
            )
    return db.captains.find_one({"user_id": oid})
