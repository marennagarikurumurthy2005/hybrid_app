import math
from typing import List, Dict


def decode_polyline(polyline_str: str) -> List[Dict]:
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


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def distance_point_to_polyline_km(point: Dict, polyline_points: List[Dict]) -> float:
    if not polyline_points:
        return 9999.0
    lat = float(point.get("lat"))
    lng = float(point.get("lng"))
    min_km = 9999.0
    for p in polyline_points:
        d = haversine_km(lat, lng, p.get("lat"), p.get("lng"))
        if d < min_km:
            min_km = d
    return min_km
