import math
import threading
from datetime import timedelta
from typing import Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from pymongo import ReturnDocument

from core.db import get_db
from core.geo_utils import ensure_captain_geo_index, to_point
from core.redis_queue import (
    enqueue_job,
    set_candidates,
    pop_candidate,
    set_offer,
    clear_offer,
    is_ws_online,
)
from core.utils import utcnow, to_object_id
from notifications import services as notification_services
from pricing import services as pricing_services


def _job_collection(job_type: str):
    db = get_db()
    if job_type == "ORDER":
        return db.orders
    if job_type == "RIDE":
        return db.rides
    raise ValueError("Invalid job type")


def _send_ws(group: str, event_type: str, payload: dict):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        group,
        {"type": event_type, "payload": payload},
    )


def _resolve_pickup_location(job_type: str, job_doc: dict):
    if job_doc.get("pickup_location"):
        return job_doc.get("pickup_location")
    db = get_db()
    if job_type == "ORDER":
        restaurant_id = job_doc.get("restaurant_id")
        if restaurant_id:
            restaurant = db.restaurants.find_one({"_id": restaurant_id})
            if restaurant and restaurant.get("location"):
                return restaurant.get("location")
    if job_type == "RIDE":
        pickup = job_doc.get("pickup") or {}
        if "lat" in pickup and "lng" in pickup:
            return to_point(pickup["lat"], pickup["lng"])
    return None


def _haversine_km(lat1, lon1, lat2, lon2):
    r = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def _idle_minutes(captain: dict):
    last_assigned = captain.get("last_assigned_at")
    if not last_assigned:
        return 120.0
    delta = utcnow() - last_assigned
    return max(delta.total_seconds() / 60.0, 0.0)


def _dispatch_score(captain: dict, pickup_location: dict, surge_multiplier: float):
    coords = captain.get("location", {}).get("coordinates", [None, None])
    if coords[0] is None or coords[1] is None:
        distance_km = 999.0
    else:
        distance_km = _haversine_km(pickup_location["coordinates"][1], pickup_location["coordinates"][0], coords[1], coords[0])

    rating = float(captain.get("average_rating") or 5.0)
    fairness = min(_idle_minutes(captain) / 60.0, 1.0)

    score = (
        distance_km * settings.DISPATCH_DISTANCE_WEIGHT * surge_multiplier
        - rating * settings.DISPATCH_RATING_WEIGHT
        - fairness * settings.DISPATCH_FAIRNESS_WEIGHT
    )
    return score


def _rank_captains(captains: list, pickup_location: dict, surge_multiplier: float):
    scored = []
    for captain in captains:
        scored.append((captain, _dispatch_score(captain, pickup_location, surge_multiplier)))
    scored.sort(key=lambda item: item[1])
    return [captain for captain, _ in scored]


def _try_batch_order(job_doc: dict, pickup_location: dict):
    db = get_db()
    radius = min(settings.CAPTAIN_MATCH_RADIUS_M, 2000)
    cursor = db.captains.find({
        "is_online": True,
        "is_verified": True,
        "is_busy": True,
        "current_job_type": "ORDER",
        "location": {
            "$near": {
                "$geometry": pickup_location,
                "$maxDistance": radius,
            }
        },
    }).limit(10)

    for captain in cursor:
        batched = captain.get("batched_order_ids") or []
        if len(batched) >= settings.CAPTAIN_MAX_BATCH_ORDERS:
            continue
        captain_id = str(captain.get("user_id"))
        if not captain_id:
            continue

        order_id = str(job_doc.get("_id"))
        db.orders.update_one(
            {"_id": job_doc["_id"]},
            {"$set": {
                "captain_id": to_object_id(captain_id),
                "status": "ASSIGNED",
                "job_status": "ASSIGNED",
                "matched_at": utcnow(),
                "batched": True,
            }},
        )
        db.captains.update_one(
            {"user_id": to_object_id(captain_id)},
            {"$addToSet": {"batched_order_ids": job_doc["_id"]}, "$set": {"last_assigned_at": utcnow()}},
        )

        user_id = str(job_doc.get("user_id")) if job_doc.get("user_id") else None
        if user_id:
            _send_ws(f"user_{user_id}", "job_assigned", {"job_id": order_id, "job_type": "ORDER", "captain_id": captain_id})
            notification_services.send_to_user(
                user_id,
                "Captain assigned",
                "A captain has been assigned to your order.",
                {"order_id": order_id},
            )

        restaurant_id = job_doc.get("restaurant_id")
        if restaurant_id:
            restaurant = db.restaurants.find_one({"_id": restaurant_id})
            if restaurant and restaurant.get("owner_id"):
                notification_services.send_to_user(
                    str(restaurant.get("owner_id")),
                    "Order assigned",
                    "A captain has been assigned for pickup.",
                    {"order_id": order_id},
                )

        _send_ws(f"captain_{captain_id}", "job_assigned", {"job_id": order_id, "job_type": "ORDER", "batched": True})
        return captain_id

    return None


def _log_matching_decision(job_type: str, job_id: str, candidate_ids: list, eta_map: dict):
    db = get_db()
    db.matching_logs.insert_one({
        "job_type": job_type,
        "job_id": to_object_id(job_id),
        "candidate_ids": [to_object_id(cid) for cid in candidate_ids if to_object_id(cid)],
        "eta_map": eta_map,
        "created_at": utcnow(),
    })


def find_nearby_captains(pickup_location: dict, radius_m: Optional[int] = None, limit: Optional[int] = None, vehicle_type: Optional[str] = None):
    ensure_captain_geo_index()
    db = get_db()
    radius = radius_m or settings.CAPTAIN_MATCH_RADIUS_M
    max_limit = limit or settings.CAPTAIN_MATCH_MAX_CANDIDATES
    query = {
        "is_online": True,
        "is_verified": True,
        "is_busy": {"$ne": True},
        "location": {
            "$near": {
                "$geometry": pickup_location,
                "$maxDistance": radius,
            }
        },
    }
    if vehicle_type:
        query["vehicle_type"] = vehicle_type
    cursor = db.captains.find(query).limit(max_limit)
    return list(cursor)


def create_job(job_type: str, job_id: str):
    collection = _job_collection(job_type)
    oid = to_object_id(job_id)
    if not oid:
        raise ValueError("Invalid job id")

    job_doc = collection.find_one({"_id": oid})
    if not job_doc:
        raise ValueError("Job not found")

    pickup_location = _resolve_pickup_location(job_type, job_doc)
    if not pickup_location:
        collection.update_one({"_id": oid}, {"$set": {"job_status": "NO_LOCATION"}})
        return []

    if job_type == "ORDER":
        batched = _try_batch_order(job_doc, pickup_location)
        if batched:
            return [batched]

    surge_multiplier = 1.0
    try:
        surge_info = pricing_services.calculate_surge(
            job_type,
            pickup_location["coordinates"][1],
            pickup_location["coordinates"][0],
            store_history=False,
        )
        surge_multiplier = float(surge_info.get("surge_multiplier", 1.0))
    except Exception:
        surge_multiplier = 1.0

    vehicle_type = job_doc.get("vehicle_type")
    captains = find_nearby_captains(pickup_location, vehicle_type=vehicle_type)
    ranked = _rank_captains(captains, pickup_location, surge_multiplier)
    eta_map = {}
    try:
        from maps import services as maps_services
        ranked, eta_map = maps_services.rank_captains_by_eta(pickup_location, ranked)
    except Exception:
        eta_map = {}
    candidate_ids = [str(captain.get("user_id")) for captain in ranked if captain.get("user_id")]

    set_candidates(job_id, candidate_ids)
    enqueue_job(job_id)

    collection.update_one(
        {"_id": oid},
        {"$set": {
            "job_status": "SEARCHING",
            "pickup_location": pickup_location,
            "current_offer": None,
            "job_attempts": 0,
            "rejected_captains": [],
        }},
    )

    _log_matching_decision(job_type, job_id, candidate_ids, eta_map)
    offer_next_captain(job_type, job_id)
    return candidate_ids


def offer_next_captain(job_type: str, job_id: str):
    collection = _job_collection(job_type)
    oid = to_object_id(job_id)
    if not oid:
        return None

    candidate_id = pop_candidate(job_id)
    if not candidate_id:
        collection.update_one(
            {"_id": oid},
            {"$set": {"job_status": "NO_CAPTAIN", "current_offer": None}},
        )
        job_doc = collection.find_one({"_id": oid})
        if job_doc and job_doc.get("user_id"):
            user_id = str(job_doc.get("user_id"))
            _send_ws(f"user_{user_id}", "job_status", {"status": "NO_CAPTAIN", "job_id": job_id})
            notification_services.send_to_user(
                user_id,
                "No captains available",
                "We could not find a nearby captain.",
                {"job_id": job_id},
            )
        return None

    expires_at = utcnow() + timedelta(seconds=settings.CAPTAIN_MATCH_TIMEOUT_SEC)
    set_offer(job_id, candidate_id, expires_at)
    collection.update_one(
        {"_id": oid},
        {"$set": {
            "job_status": "OFFERED",
            "current_offer": {
                "captain_id": to_object_id(candidate_id),
                "expires_at": expires_at,
            },
        }, "$inc": {"job_attempts": 1}},
    )

    payload = {
        "job_id": job_id,
        "job_type": job_type,
        "expires_at": expires_at.isoformat(),
    }
    _send_ws(f"captain_{candidate_id}", "job_offer", payload)

    db = get_db()
    db.matching_logs.insert_one({
        "job_type": job_type,
        "job_id": to_object_id(job_id),
        "offered_captain_id": to_object_id(candidate_id),
        "expires_at": expires_at,
        "created_at": utcnow(),
    })

    if not is_ws_online("captain", candidate_id):
        notification_services.send_to_user(
            candidate_id,
            "New job offer",
            f"New {job_type} job available.",
            {"job_id": job_id, "job_type": job_type},
        )

    timer = threading.Timer(
        settings.CAPTAIN_MATCH_TIMEOUT_SEC,
        handle_offer_timeout,
        args=(job_type, job_id, candidate_id),
    )
    timer.daemon = True
    timer.start()
    return candidate_id


def handle_offer_timeout(job_type: str, job_id: str, captain_id: str):
    collection = _job_collection(job_type)
    oid = to_object_id(job_id)
    if not oid:
        return
    job_doc = collection.find_one({"_id": oid})
    if not job_doc:
        return
    if job_doc.get("job_status") in {"ASSIGNED", "COMPLETED"}:
        return
    current_offer = job_doc.get("current_offer") or {}
    offered = str(current_offer.get("captain_id")) if current_offer.get("captain_id") else None
    if offered != str(captain_id):
        return

    collection.update_one(
        {"_id": oid},
        {"$addToSet": {"rejected_captains": to_object_id(captain_id)}, "$set": {"current_offer": None}},
    )
    db = get_db()
    db.captains.update_one(
        {"user_id": to_object_id(captain_id)},
        {"$inc": {"cancellations": 1}},
    )
    clear_offer(job_id)
    offer_next_captain(job_type, job_id)


def accept_job(job_type: str, job_id: str, captain_id: str):
    db = get_db()
    collection = _job_collection(job_type)
    oid = to_object_id(job_id)
    captain_oid = to_object_id(captain_id)
    if not oid or not captain_oid:
        raise ValueError("Invalid job or captain id")

    job_doc = collection.find_one({"_id": oid})
    if not job_doc:
        raise ValueError("Job not found")

    current_offer = job_doc.get("current_offer") or {}
    offered = current_offer.get("captain_id")
    if not offered or str(offered) != str(captain_oid):
        raise ValueError("Job not offered to this captain")

    captain_query = {"user_id": captain_oid, "is_online": True, "is_busy": False, "is_verified": True}
    job_vehicle_type = job_doc.get("vehicle_type")
    if job_vehicle_type:
        captain_query["vehicle_type"] = job_vehicle_type
    captain = db.captains.find_one_and_update(
        captain_query,
        {"$set": {
            "is_busy": True,
            "current_job_id": oid,
            "current_job_type": job_type,
            "current_job": {"type": job_type, "id": job_id},
            "last_assigned_at": utcnow(),
            "last_seen": utcnow(),
        }},
        return_document=ReturnDocument.AFTER,
    )
    if not captain:
        raise ValueError("Captain unavailable")

    status = "ASSIGNED"
    if job_type == "ORDER":
        status = "ASSIGNED"
    if job_type == "RIDE":
        status = "ASSIGNED"

    collection.update_one(
        {"_id": oid},
        {"$set": {
            "captain_id": captain_oid,
            "status": status,
            "job_status": "ASSIGNED",
            "matched_at": utcnow(),
            "current_offer": None,
        }},
    )
    clear_offer(job_id)

    user_id = str(job_doc.get("user_id")) if job_doc.get("user_id") else None
    if user_id:
        _send_ws(f"user_{user_id}", "job_assigned", {"job_id": job_id, "job_type": job_type, "captain_id": captain_id})
        notification_services.send_to_user(
            user_id,
            "Captain assigned",
            "A captain has been assigned to your request.",
            {"job_id": job_id, "job_type": job_type},
        )

    if job_type == "ORDER":
        restaurant_id = job_doc.get("restaurant_id")
        if restaurant_id:
            restaurant = db.restaurants.find_one({"_id": restaurant_id})
            if restaurant and restaurant.get("owner_id"):
                notification_services.send_to_user(
                    str(restaurant.get("owner_id")),
                    "Order assigned",
                    "A captain has been assigned for pickup.",
                    {"order_id": job_id},
                )
        db.captains.update_one(
            {"user_id": captain_oid},
            {"$addToSet": {"batched_order_ids": oid}},
        )

    _send_ws(f"captain_{captain_id}", "job_assigned", {"job_id": job_id, "job_type": job_type})
    return collection.find_one({"_id": oid})


def reject_job(job_type: str, job_id: str, captain_id: str):
    collection = _job_collection(job_type)
    oid = to_object_id(job_id)
    captain_oid = to_object_id(captain_id)
    if not oid or not captain_oid:
        raise ValueError("Invalid job or captain id")

    job_doc = collection.find_one({"_id": oid})
    if not job_doc:
        raise ValueError("Job not found")

    current_offer = job_doc.get("current_offer") or {}
    offered = current_offer.get("captain_id")
    if not offered or str(offered) != str(captain_oid):
        raise ValueError("Job not offered to this captain")

    collection.update_one(
        {"_id": oid},
        {"$addToSet": {"rejected_captains": captain_oid}, "$set": {"current_offer": None, "job_status": "SEARCHING"}},
    )
    db = get_db()
    db.captains.update_one(
        {"user_id": captain_oid},
        {"$inc": {"cancellations": 1}},
    )
    clear_offer(job_id)
    offer_next_captain(job_type, job_id)
    return True


def complete_job(job_type: str, job_id: str, captain_id: str):
    db = get_db()
    collection = _job_collection(job_type)
    oid = to_object_id(job_id)
    captain_oid = to_object_id(captain_id)
    if not oid or not captain_oid:
        raise ValueError("Invalid job or captain id")

    job_doc = collection.find_one({"_id": oid})
    if not job_doc:
        raise ValueError("Job not found")

    assigned = job_doc.get("captain_id")
    if not assigned or str(assigned) != str(captain_oid):
        raise ValueError("Captain not assigned to this job")

    from captains import services as captain_services
    captain_services.complete_job(captain_id, job_type, job_id)

    db.captains.update_one(
        {"user_id": captain_oid},
        {"$set": {"is_busy": False, "current_job_id": None, "current_job_type": None, "current_job": None}},
    )

    if job_type == "ORDER":
        db.captains.update_one(
            {"user_id": captain_oid},
            {"$pull": {"batched_order_ids": oid}},
        )
        captain_doc = db.captains.find_one({"user_id": captain_oid})
        remaining = captain_doc.get("batched_order_ids") if captain_doc else []
        if remaining:
            db.captains.update_one(
                {"user_id": captain_oid},
                {"$set": {"is_busy": True, "current_job_id": remaining[0], "current_job_type": "ORDER", "current_job": {"type": "ORDER", "id": str(remaining[0])}}},
            )

    collection.update_one(
        {"_id": oid},
        {"$set": {"job_status": "COMPLETED"}},
    )

    db.captains.update_one(
        {"user_id": captain_oid},
        {"$inc": {"total_trips": 1}},
    )

    user_id = str(job_doc.get("user_id")) if job_doc.get("user_id") else None
    if user_id:
        _send_ws(f"user_{user_id}", "job_status", {"status": "COMPLETED", "job_id": job_id})

    return collection.find_one({"_id": oid})


def broadcast_location(job_type: str, job_id: str, captain_id: str, lat: float, lng: float):
    collection = _job_collection(job_type)
    oid = to_object_id(job_id)
    if not oid:
        return
    job_doc = collection.find_one({"_id": oid})
    if not job_doc:
        return
    user_id = str(job_doc.get("user_id")) if job_doc.get("user_id") else None
    if not user_id:
        return
    payload = {
        "job_id": job_id,
        "job_type": job_type,
        "captain_id": captain_id,
        "location": {"lat": lat, "lng": lng},
    }
    _send_ws(f"user_{user_id}", "location_update", payload)
    _send_ws(f"{job_type.lower()}_{job_id}", "location_update", payload)
