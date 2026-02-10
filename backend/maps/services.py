import hashlib
import json
from datetime import timedelta
from typing import List, Optional

import requests
from django.conf import settings
from pymongo import ASCENDING

from core.db import get_db
from core.geo_utils import ensure_captain_geo_index
from core.utils import utcnow

_index_ready = False


def ensure_indexes():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.routes_cache.create_index([("cache_key", ASCENDING)], unique=True, name="routes_cache_key")
    db.routes_cache.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0, name="routes_cache_ttl")
    _index_ready = True


def _cache_key(payload: dict):
    raw = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _decode_polyline(polyline_str: str):
    index = 0
    lat = 0
    lng = 0
    coordinates = []

    while index < len(polyline_str):
        result = 0
        shift = 0
        while True:
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        delta_lat = ~(result >> 1) if result & 1 else result >> 1
        lat += delta_lat

        result = 0
        shift = 0
        while True:
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        delta_lng = ~(result >> 1) if result & 1 else result >> 1
        lng += delta_lng

        coordinates.append({"lat": lat / 1e5, "lng": lng / 1e5})

    return coordinates


def _call_google(endpoint: str, params: dict):
    if not settings.GOOGLE_MAPS_KEY:
        raise ValueError("GOOGLE_MAPS_KEY not configured")
    params["key"] = settings.GOOGLE_MAPS_KEY
    resp = requests.get(endpoint, params=params, timeout=10)
    data = resp.json()
    status = data.get("status")
    if status != "OK":
        raise ValueError(data.get("error_message") or f"Maps API error: {status}")
    return data


def get_route(origin: dict, destination: dict, mode: str = "driving"):
    ensure_indexes()
    cache_payload = {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "traffic_model": "best_guess",
        "departure_time": "now",
    }
    key = _cache_key(cache_payload)
    db = get_db()
    cached = db.routes_cache.find_one({"cache_key": key, "expires_at": {"$gt": utcnow()}})
    if cached:
        cached["cached"] = True
        return cached

    params = {
        "origin": f"{origin['lat']},{origin['lng']}",
        "destination": f"{destination['lat']},{destination['lng']}",
        "mode": mode,
        "departure_time": "now",
        "traffic_model": "best_guess",
    }
    data = _call_google("https://maps.googleapis.com/maps/api/directions/json", params)

    route = data["routes"][0]
    leg = route["legs"][0]
    polyline = route["overview_polyline"]["points"]
    points = _decode_polyline(polyline)

    doc = {
        "cache_key": key,
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "distance_m": leg["distance"]["value"],
        "duration_s": leg["duration"]["value"],
        "duration_in_traffic_s": leg.get("duration_in_traffic", {}).get("value"),
        "polyline": polyline,
        "points": points,
        "summary": route.get("summary"),
        "created_at": utcnow(),
        "expires_at": utcnow() + timedelta(minutes=settings.MAPS_CACHE_TTL_MIN),
    }
    db.routes_cache.update_one({"cache_key": key}, {"$set": doc}, upsert=True)
    doc["cached"] = False
    return doc


def get_eta(origin: dict, destination: dict, mode: str = "driving"):
    params = {
        "origins": f"{origin['lat']},{origin['lng']}",
        "destinations": f"{destination['lat']},{destination['lng']}",
        "mode": mode,
        "departure_time": "now",
        "traffic_model": "best_guess",
    }
    data = _call_google("https://maps.googleapis.com/maps/api/distancematrix/json", params)
    element = data["rows"][0]["elements"][0]
    if element.get("status") != "OK":
        raise ValueError("No route found")
    return {
        "origin": origin,
        "destination": destination,
        "distance_m": element["distance"]["value"],
        "duration_s": element["duration"]["value"],
        "duration_in_traffic_s": element.get("duration_in_traffic", {}).get("value"),
    }


def rank_captains_by_eta(pickup_location: dict, captains: List[dict], mode: str = "driving"):
    if not captains:
        return [], {}
    origins = []
    origin_captains = []
    no_location = []
    for captain in captains:
        coords = captain.get("location", {}).get("coordinates")
        if not coords:
            no_location.append(captain)
            continue
        origins.append(f"{coords[1]},{coords[0]}")
        origin_captains.append(captain)

    if not origins:
        return captains, {}

    eta_map = {}
    chunk_size = 25
    for idx in range(0, len(origins), chunk_size):
        chunk_origins = origins[idx:idx + chunk_size]
        params = {
            "origins": "|".join(chunk_origins),
            "destinations": f"{pickup_location['coordinates'][1]},{pickup_location['coordinates'][0]}",
            "mode": mode,
            "departure_time": "now",
            "traffic_model": "best_guess",
        }
        data = _call_google("https://maps.googleapis.com/maps/api/distancematrix/json", params)
        rows = data.get("rows", [])
        for row_idx, row in enumerate(rows):
            elements = row.get("elements", [])
            if not elements:
                continue
            element = elements[0]
            if element.get("status") != "OK":
                continue
            duration = element.get("duration_in_traffic", element.get("duration"))
            captain = origin_captains[idx + row_idx]
            eta_map[str(captain.get("user_id"))] = duration.get("value")

    ordered = sorted(origin_captains, key=lambda c: eta_map.get(str(c.get("user_id")), 10**9))
    ordered.extend(no_location)
    return ordered, eta_map


def find_nearby_captains(lat: float, lng: float, radius_m: int = 5000, limit: int = 20):
    ensure_captain_geo_index()
    db = get_db()
    cursor = db.captains.find({
        "is_online": True,
        "is_verified": True,
        "is_busy": {"$ne": True},
        "location": {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                "$maxDistance": radius_m,
            }
        },
    }).limit(limit)
    return list(cursor)
