from typing import Dict
from pymongo import ASCENDING

from core.db import get_db
from core.utils import utcnow
from maps import services as maps_services

_index_ready = False


def ensure_indexes():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.eta_logs.create_index([("created_at", -1)], name="eta_logs_created_at")
    _index_ready = True


def predict_eta(payload: Dict):
    ensure_indexes()
    origin = {"lat": payload["origin_lat"], "lng": payload["origin_lng"]}
    destination = {"lat": payload["destination_lat"], "lng": payload["destination_lng"]}
    base = maps_services.get_eta(origin, destination, mode="driving")

    prep_time_min = int(payload.get("prep_time_min", 0))
    batch_size = int(payload.get("batch_size", 1))
    traffic_factor = float(payload.get("traffic_factor", 1.0))
    weather_factor = float(payload.get("weather_factor", 1.0))

    buffer_s = prep_time_min * 60
    batch_buffer_s = max(0, batch_size - 1) * 120
    travel_s = int(base.get("duration_in_traffic_s") or base.get("duration_s") or 0)
    adjusted_s = int(travel_s * traffic_factor * weather_factor) + buffer_s + batch_buffer_s

    db = get_db()
    log_doc = {
        "origin": origin,
        "destination": destination,
        "base_duration_s": travel_s,
        "adjusted_duration_s": adjusted_s,
        "prep_time_min": prep_time_min,
        "batch_size": batch_size,
        "traffic_factor": traffic_factor,
        "weather_factor": weather_factor,
        "created_at": utcnow(),
    }
    db.eta_logs.insert_one(log_doc)
    return {
        "base_duration_s": travel_s,
        "adjusted_duration_s": adjusted_s,
        "distance_m": base.get("distance_m"),
        "prep_time_min": prep_time_min,
        "batch_size": batch_size,
    }
