from core.db import get_db

_index_ready = False


def ensure_captain_geo_index():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.captains.create_index([("location", "2dsphere")], name="captain_location_2dsphere")
    _index_ready = True


def to_point(lat: float, lng: float):
    return {"type": "Point", "coordinates": [float(lng), float(lat)]}
