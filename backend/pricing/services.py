from datetime import datetime
from typing import Optional

from django.conf import settings
from pymongo import ASCENDING

from core.db import get_db
from core.geo_utils import ensure_captain_geo_index, to_point
from core.utils import utcnow

_index_ready = False


def ensure_indexes():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.surge_history.create_index([("created_at", ASCENDING)], name="surge_created_at")
    db.surge_history.create_index([("job_type", ASCENDING)], name="surge_job_type")
    db.orders.create_index([("pickup_location", "2dsphere")], name="orders_pickup_2dsphere")
    db.rides.create_index([("pickup_location", "2dsphere")], name="rides_pickup_2dsphere")
    _index_ready = True


def _time_factor(now: Optional[datetime] = None):
    now = now or datetime.utcnow()
    hour = now.hour
    if 7 <= hour <= 10 or 12 <= hour <= 14 or 18 <= hour <= 22:
        return 0.2
    if 23 <= hour or hour <= 5:
        return 0.1
    return 0.0


def _count_demand(job_type: str, location: dict, radius_m: int):
    db = get_db()
    if job_type == "ORDER":
        return db.orders.count_documents({
            "job_status": {"$in": ["CREATED", "SEARCHING", "OFFERED"]},
            "pickup_location": {
                "$near": {"$geometry": location, "$maxDistance": radius_m}
            },
        })
    if job_type == "RIDE":
        return db.rides.count_documents({
            "job_status": {"$in": ["CREATED", "SEARCHING", "OFFERED"]},
            "pickup_location": {
                "$near": {"$geometry": location, "$maxDistance": radius_m}
            },
        })
    return 0


def _count_supply(location: dict, radius_m: int):
    ensure_captain_geo_index()
    db = get_db()
    return db.captains.count_documents({
        "is_online": True,
        "is_verified": True,
        "is_busy": {"$ne": True},
        "location": {
            "$near": {"$geometry": location, "$maxDistance": radius_m}
        },
    })


def calculate_surge(job_type: str, lat: float, lng: float, store_history: bool = True):
    ensure_indexes()
    location = to_point(lat, lng)
    radius = settings.CAPTAIN_MATCH_RADIUS_M
    demand = _count_demand(job_type, location, radius)
    supply = _count_supply(location, radius)
    ratio = float(demand) / max(float(supply), 1.0)

    time_factor = _time_factor()
    weather_factor = max(settings.WEATHER_FACTOR, 0.8)

    demand_factor = min(1.2, ratio * 0.35)
    surge_multiplier = 1.0 + demand_factor + time_factor + max(0.0, weather_factor - 1.0)
    surge_multiplier = max(1.0, min(3.0, surge_multiplier))

    data = {
        "job_type": job_type,
        "location": location,
        "demand": demand,
        "supply": supply,
        "ratio": ratio,
        "time_factor": time_factor,
        "weather_factor": weather_factor,
        "surge_multiplier": round(surge_multiplier, 2),
        "created_at": utcnow(),
    }
    if store_history:
        db = get_db()
        db.surge_history.insert_one(data)

    return data


def apply_surge(amount: int, multiplier: float):
    return int(round(amount * multiplier))
