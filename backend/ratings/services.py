from typing import Optional
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from core.db import get_db
from core.utils import utcnow, to_object_id

_index_ready = False


def ensure_indexes():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.captain_ratings.create_index([("captain_id", ASCENDING), ("created_at", ASCENDING)], name="captain_ratings_by_captain")
    db.captain_ratings.create_index([("job_id", ASCENDING), ("user_id", ASCENDING)], unique=True, name="captain_ratings_unique_job_user")
    _index_ready = True


def _get_job(job_type: str, job_id: str):
    db = get_db()
    oid = to_object_id(job_id)
    if not oid:
        return None
    if job_type == "ORDER":
        return db.orders.find_one({"_id": oid})
    if job_type == "RIDE":
        return db.rides.find_one({"_id": oid})
    return None


def rate_captain(user_id: str, job_type: str, job_id: str, rating: int, comment: Optional[str] = None):
    ensure_indexes()
    db = get_db()
    job_doc = _get_job(job_type, job_id)
    if not job_doc:
        raise ValueError("Job not found")

    if str(job_doc.get("user_id")) != str(user_id):
        raise ValueError("Not allowed to rate this job")

    if job_type == "ORDER" and job_doc.get("status") != "DELIVERED":
        raise ValueError("Order is not completed")
    if job_type == "RIDE" and job_doc.get("status") != "COMPLETED":
        raise ValueError("Ride is not completed")

    captain_id = job_doc.get("captain_id")
    if not captain_id:
        raise ValueError("Captain not assigned")

    rating_doc = {
        "job_type": job_type,
        "job_id": to_object_id(job_id),
        "user_id": to_object_id(user_id),
        "captain_id": captain_id,
        "rating": int(rating),
        "comment": comment,
        "created_at": utcnow(),
    }
    try:
        db.captain_ratings.insert_one(rating_doc)
    except DuplicateKeyError as exc:
        raise ValueError("Rating already submitted for this job") from exc

    captain = db.captains.find_one({"user_id": captain_id})
    if captain:
        total_ratings = int(captain.get("total_ratings", 0))
        avg = float(captain.get("average_rating", 5.0))
        new_avg = round(((avg * total_ratings) + rating) / (total_ratings + 1), 2)
        db.captains.update_one(
            {"user_id": captain_id},
            {"$set": {"average_rating": new_avg}, "$inc": {"total_ratings": 1}},
        )

    return rating_doc


def get_captain_stats(captain_id: str):
    db = get_db()
    cid = to_object_id(captain_id)
    if not cid:
        return None
    captain = db.captains.find_one({"user_id": cid})
    if not captain:
        return None

    total_trips = int(captain.get("total_trips", 0))
    cancellations = int(captain.get("cancellations", 0))
    cancellation_rate = round(cancellations / max(total_trips, 1), 3)

    return {
        "captain_id": str(captain.get("user_id")),
        "average_rating": float(captain.get("average_rating", 5.0)),
        "total_ratings": int(captain.get("total_ratings", 0)),
        "total_trips": total_trips,
        "cancellation_rate": cancellation_rate,
    }
