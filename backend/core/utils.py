from datetime import datetime, timezone
from bson import ObjectId


def utcnow():
    return datetime.now(timezone.utc)


def to_object_id(value):
    try:
        return ObjectId(str(value))
    except Exception:
        return None


def normalize(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize(v) for v in value]
    return value


def serialize_doc(doc):
    if doc is None:
        return None
    return normalize(doc)
