import logging
from pymongo import ReturnDocument

from core.db import get_db
from core.utils import utcnow, to_object_id
from core.geo_utils import to_point, haversine_km
from core.vehicles import is_ev_vehicle
from notifications import services as notification_services
from django.conf import settings

logger = logging.getLogger(__name__)

CAPTAIN_PROFILE_EDITABLE_FIELDS = {
    "name",
    "avatar_url",
    "vehicle_number",
    "vehicle_type",
    "home_location",
    "bio",
}

CAPTAIN_PROFILE_BLOCKED_FIELDS = {
    "_id",
    "user_id",
    "phone",
    "role",
    "wallet_balance",
    "ratings",
    "average_rating",
    "total_ratings",
    "earnings",
    "is_verified",
    "verified_at",
    "verification_reason",
    "is_online",
    "is_busy",
    "is_active",
    "current_job_id",
    "current_job_type",
    "current_job",
    "batched_order_ids",
    "go_home_mode",
    "go_home_activated_at",
    "go_home_eta_s",
    "go_home_distance_m",
    "go_home_updated_at",
    "location",
    "last_seen",
    "last_assigned_at",
    "created_at",
    "updated_at",
    "deleted_at",
}


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
        "vehicle_type": None,
        "is_ev": False,
        "vehicle_number": None,
        "vehicle_brand": None,
        "license_number": None,
        "rc_image": None,
        "license_image": None,
        "is_verified": False,
        "verified_at": None,
        "verification_reason": None,
        "go_home_mode": False,
        "home_location": None,
        "go_home_activated_at": None,
        "go_home_eta_s": None,
        "go_home_distance_m": None,
        "go_home_updated_at": None,
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
    captain = db.captains.find_one({"user_id": oid})
    if not captain:
        return None
    if is_online and not captain.get("is_verified", False):
        raise ValueError("Captain is not verified")
    update = {"is_online": is_online, "last_seen": utcnow()}
    if not is_online:
        update["is_busy"] = False
        update["current_job_id"] = None
        update["current_job_type"] = None
        update["current_job"] = None
        update["go_home_mode"] = False
        update["home_location"] = None
        update["go_home_activated_at"] = None
    db.captains.update_one({"user_id": oid}, {"$set": update})
    return db.captains.find_one({"user_id": oid})


def update_location(user_id: str, lat: float, lng: float):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    existing = db.captains.find_one({"user_id": oid})
    if existing and existing.get("location") and existing.get("last_seen"):
        coords = existing.get("location", {}).get("coordinates")
        if coords and coords[0] is not None and coords[1] is not None:
            last_lat = coords[1]
            last_lng = coords[0]
            dist_km = haversine_km(last_lat, last_lng, lat, lng)
            delta_s = max((utcnow() - existing.get("last_seen")).total_seconds(), 1)
            speed_kmph = (dist_km / (delta_s / 3600.0)) if delta_s > 0 else 0
            if speed_kmph > settings.GO_HOME_MAX_SPEED_KMPH:
                db.trust_logs.insert_one({
                    "user_id": oid,
                    "findings": [{"type": "GPS_JUMP", "detail": f"speed={speed_kmph:.2f}km/h"}],
                    "created_at": utcnow(),
                })
                return existing
    db.captains.update_one(
        {"user_id": oid},
        {"$set": {"location": to_point(lat, lng), "last_seen": utcnow()}},
    )
    updated = db.captains.find_one({"user_id": oid})
    if updated and updated.get("go_home_mode") and updated.get("home_location"):
        try:
            from maps import services as maps_services
            home_coords = updated.get("home_location", {}).get("coordinates")
            if home_coords:
                eta = maps_services.get_eta(
                    {"lat": lat, "lng": lng},
                    {"lat": home_coords[1], "lng": home_coords[0]},
                )
                db.captains.update_one(
                    {"user_id": oid},
                    {"$set": {
                        "go_home_eta_s": int(eta.get("duration_in_traffic_s") or eta.get("duration_s") or 0),
                        "go_home_distance_m": int(eta.get("distance_m") or 0),
                        "go_home_updated_at": utcnow(),
                    }},
                )
        except Exception:
            pass
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


def register_vehicle(user_id: str, vehicle: dict):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    existing = db.captains.find_one({"user_id": oid})
    if not existing:
        existing = ensure_captain_profile(user_id)
    vehicle_type = vehicle.get("vehicle_type")
    update = {
        "vehicle_type": vehicle_type,
        "is_ev": bool(is_ev_vehicle(vehicle_type)),
        "vehicle_number": vehicle.get("vehicle_number"),
        "vehicle_brand": vehicle.get("vehicle_brand"),
        "license_number": vehicle.get("license_number"),
        "rc_image": vehicle.get("rc_image"),
        "license_image": vehicle.get("license_image"),
        "is_verified": False,
        "verified_at": None,
        "verification_reason": None,
        "is_online": False,
    }
    db.captains.update_one({"user_id": oid}, {"$set": update})
    return db.captains.find_one({"user_id": oid})


def get_vehicle(user_id: str):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    captain = db.captains.find_one({"user_id": oid})
    if not captain:
        return None
    return {
        "vehicle_type": captain.get("vehicle_type"),
        "is_ev": bool(captain.get("is_ev", False)),
        "vehicle_number": captain.get("vehicle_number"),
        "vehicle_brand": captain.get("vehicle_brand"),
        "license_number": captain.get("license_number"),
        "rc_image": captain.get("rc_image"),
        "license_image": captain.get("license_image"),
        "is_verified": captain.get("is_verified", False),
    }


def update_captain_profile(user_id: str, updates: dict):
    if not updates:
        return None
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    existing = db.captains.find_one({"user_id": oid})
    if not existing:
        ensure_captain_profile(user_id)
    if "home_location" in updates:
        home_location = updates.get("home_location")
        if home_location:
            updates["home_location"] = to_point(home_location.get("lat"), home_location.get("lng"))
        else:
            updates["home_location"] = None
    if "vehicle_type" in updates:
        vehicle_type = updates.get("vehicle_type")
        if not vehicle_type:
            updates["vehicle_type"] = None
            updates["is_ev"] = False
        else:
            updates["is_ev"] = bool(is_ev_vehicle(vehicle_type))
    updated = db.captains.find_one_and_update(
        {"user_id": oid},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    if updated:
        logger.info("captain_profile_updated user_id=%s fields=%s", user_id, sorted(updates.keys()))
    return updated


def enable_go_home(user_id: str, lat: float, lng: float):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    update = {
        "go_home_mode": True,
        "home_location": to_point(lat, lng),
        "go_home_activated_at": utcnow(),
    }
    db.captains.update_one({"user_id": oid}, {"$set": update})
    return db.captains.find_one({"user_id": oid})


def disable_go_home(user_id: str):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    db.captains.update_one(
        {"user_id": oid},
        {"$set": {"go_home_mode": False, "home_location": None, "go_home_activated_at": None}},
    )
    return db.captains.find_one({"user_id": oid})


def assign_captain_stub(job_type: str, job_id: str):
    db = get_db()
    from vehicles import services as vehicle_services
    pipeline = [
        {
            "$match": {
                "is_online": True,
                "is_verified": True,
                "is_busy": False,
                "$or": [
                    {"current_job_id": None},
                    {"current_job_id": {"$exists": False}},
                ],
            }
        },
        {"$sample": {"size": 1}},
    ]
    if job_type == "ORDER":
        allowed = vehicle_services.get_food_allowed_vehicles()
        if allowed:
            pipeline[0]["$match"]["vehicle_type"] = {"$in": allowed}
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
        try:
            from orders import state_machine as order_state
            order_state.set_order_status(job_id, "DELIVERED", reason="COMPLETED")
        except Exception:
            db.orders.update_one(
                {"_id": order_oid},
                {"$set": {"status": "DELIVERED"}},
            )
        if order_doc and order_doc.get("payment_mode") == "COD":
            db.orders.update_one(
                {"_id": order_oid},
                {"$set": {"is_paid": True}},
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
        try:
            from rides import state_machine as ride_state
            ride_state.set_ride_status(job_id, "COMPLETED", reason="COMPLETED")
        except Exception:
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
