import math

from core.db import get_db

_index_ready = False


def ensure_captain_geo_index():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.captains.create_index([("location", "2dsphere")], name="captain_location_2dsphere")
    db.captains.create_index([("home_location", "2dsphere")], name="captain_home_location_2dsphere")
    _index_ready = True


def to_point(lat: float, lng: float):
    return {"type": "Point", "coordinates": [float(lng), float(lat)]}


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c
