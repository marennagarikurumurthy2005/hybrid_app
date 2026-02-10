from typing import Dict
from pymongo import ASCENDING
from django.conf import settings

from core.db import get_db
from core.utils import utcnow, to_object_id
from core.vehicles import normalize_vehicle_type

_index_ready = False


def ensure_indexes():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.vehicle_rules.create_index([("active", ASCENDING)], name="vehicle_rules_active")
    db.vehicles.create_index([("captain_id", ASCENDING)], unique=True, name="vehicles_captain")
    _index_ready = True


def get_rules() -> Dict:
    ensure_indexes()
    db = get_db()
    doc = db.vehicle_rules.find_one({"active": True})
    if doc:
        return doc.get("rules", {})
    return {
        "food_allowed_vehicles": settings.FOOD_ALLOWED_VEHICLES,
        "ev_reward_percentage": settings.EV_REWARD_PERCENTAGE,
        "ev_bonus_multiplier": float(getattr(settings, "EV_BONUS_MULTIPLIER", 1.0)),
    }


def set_rules(rules: Dict):
    ensure_indexes()
    db = get_db()
    db.vehicle_rules.update_one(
        {"active": True},
        {"$set": {"rules": rules, "active": True, "updated_at": utcnow()}},
        upsert=True,
    )
    return get_rules()


def register_vehicle(captain_id: str, vehicle: Dict):
    ensure_indexes()
    db = get_db()
    doc = vehicle.copy()
    doc["captain_id"] = to_object_id(captain_id)
    doc["updated_at"] = utcnow()
    db.vehicles.update_one({"captain_id": doc["captain_id"]}, {"$set": doc}, upsert=True)
    return db.vehicles.find_one({"captain_id": doc["captain_id"]})


def get_food_allowed_vehicles():
    rules = get_rules()
    raw = rules.get("food_allowed_vehicles", [])
    normalized = [normalize_vehicle_type(v) for v in raw if normalize_vehicle_type(v)]
    return normalized


def get_ev_reward_percentage():
    rules = get_rules()
    return float(rules.get("ev_reward_percentage", settings.EV_REWARD_PERCENTAGE))


def get_ev_bonus_multiplier():
    rules = get_rules()
    return float(rules.get("ev_bonus_multiplier", 1.0))
