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
    db.devices.create_index([("device_id", ASCENDING)], name="devices_device_id")
    db.devices.create_index([("user_id", ASCENDING)], name="devices_user")
    db.trust_logs.create_index([("created_at", -1)], name="trust_logs_created_at")
    _index_ready = True


def register_device(user_id: str, device_id: str, platform: Optional[str] = None, fingerprint: Optional[str] = None, ip: Optional[str] = None, meta: Optional[dict] = None):
    ensure_indexes()
    db = get_db()
    doc = {
        "user_id": to_object_id(user_id),
        "device_id": device_id,
        "platform": platform,
        "fingerprint": fingerprint,
        "ip": ip,
        "meta": meta or {},
        "created_at": utcnow(),
    }
    db.devices.update_one({"device_id": device_id, "user_id": to_object_id(user_id)}, {"$set": doc}, upsert=True)
    if meta:
        findings = []
        if meta.get("mock_location") is True:
            findings.append({"type": "MOCK_LOCATION", "detail": "mock_location flag"})
        speed = meta.get("location_speed_kmh")
        if speed and float(speed) > 200:
            findings.append({"type": "SPEED_ANOMALY", "detail": f"speed={speed}"})
        if findings:
            db.trust_logs.insert_one({
                "user_id": to_object_id(user_id),
                "findings": findings,
                "created_at": utcnow(),
            })
    return db.devices.find_one({"device_id": device_id, "user_id": to_object_id(user_id)})


def scan_user(user_id: Optional[str] = None):
    ensure_indexes()
    db = get_db()
    query = {}
    if user_id:
        query["user_id"] = to_object_id(user_id)
    devices = list(db.devices.find(query))
    findings = []
    device_ids = {d.get("device_id") for d in devices if d.get("device_id")}
    if device_ids:
        for device_id in device_ids:
            users = list(db.devices.find({"device_id": device_id}))
            user_ids = {str(u.get("user_id")) for u in users if u.get("user_id")}
            if len(user_ids) > 1:
                findings.append({"device_id": device_id, "type": "DUPLICATE_DEVICE", "users": list(user_ids)})
    if findings:
        db.trust_logs.insert_one({"user_id": to_object_id(user_id) if user_id else None, "findings": findings, "created_at": utcnow()})
    return {"findings": findings, "device_count": len(devices)}
