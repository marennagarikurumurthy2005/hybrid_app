import hashlib
from typing import List
from pymongo import ASCENDING

from core.db import get_db
from core.utils import utcnow, to_object_id
from recommendations import services as recommendation_services

_index_ready = False


def ensure_indexes():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.engagement_logs.create_index([("created_at", -1)], name="engagement_logs_created_at")
    db.experiments.create_index([("experiment_key", ASCENDING)], name="experiments_key")
    _index_ready = True


def assign_experiment(user_id: str, experiment_key: str, variants: List[str]):
    ensure_indexes()
    if not variants:
        raise ValueError("No variants provided")
    payload = f"{user_id}:{experiment_key}".encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    idx = int(digest, 16) % len(variants)
    variant = variants[idx]

    db = get_db()
    db.experiments.update_one(
        {"user_id": to_object_id(user_id), "experiment_key": experiment_key},
        {"$set": {"variant": variant, "variants": variants, "assigned_at": utcnow()}},
        upsert=True,
    )
    return {"experiment_key": experiment_key, "variant": variant}


def personalized_feed(user_id: str, limit: int = 50):
    ensure_indexes()
    recs = recommendation_services.list_user_recommendations(limit=limit)
    db = get_db()
    db.engagement_logs.insert_one({
        "user_id": to_object_id(user_id),
        "event": "FEED_VIEW",
        "created_at": utcnow(),
    })
    return recs
