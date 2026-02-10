import threading
from datetime import timedelta

from django.conf import settings
from pymongo import ReturnDocument

from core.db import get_db
from core.utils import utcnow, to_object_id

RIDE_STATUSES = {
    "PENDING_PAYMENT",
    "REQUESTED",
    "ASSIGNED",
    "COMPLETED",
    "CANCELLED",
    "FAILED",
}

RIDE_STATUS_TRANSITIONS = {
    "PENDING_PAYMENT": {"REQUESTED", "FAILED", "CANCELLED"},
    "REQUESTED": {"ASSIGNED", "CANCELLED"},
    "ASSIGNED": {"COMPLETED", "CANCELLED"},
    "COMPLETED": set(),
    "CANCELLED": set(),
    "FAILED": set(),
}


def _transition_allowed(current_status: str, new_status: str) -> bool:
    if not current_status:
        return True
    allowed = RIDE_STATUS_TRANSITIONS.get(current_status)
    if allowed is None:
        return True
    return new_status in allowed


def set_ride_status(ride_id: str, new_status: str, reason: str = None):
    if new_status not in RIDE_STATUSES:
        raise ValueError("Invalid ride status")
    db = get_db()
    oid = to_object_id(ride_id)
    if not oid:
        return None
    ride = db.rides.find_one({"_id": oid})
    if not ride:
        return None
    current = ride.get("status")
    if current == new_status:
        return ride
    if not _transition_allowed(current, new_status):
        raise ValueError(f"Invalid transition {current} -> {new_status}")
    entry = {
        "from": current,
        "to": new_status,
        "reason": reason,
        "at": utcnow(),
    }
    update = {
        "status": new_status,
        "status_updated_at": utcnow(),
    }
    if reason:
        update["status_reason"] = reason
    return db.rides.find_one_and_update(
        {"_id": oid},
        {"$set": update, "$push": {"status_history": entry}},
        return_document=ReturnDocument.AFTER,
    )


def ensure_ride_sla(ride_doc: dict):
    if not ride_doc:
        return None
    if ride_doc.get("sla"):
        return ride_doc
    created_at = ride_doc.get("created_at") or utcnow()
    assign_by = created_at + timedelta(seconds=int(getattr(settings, "RIDE_ASSIGN_TIMEOUT_SEC", 300)))
    complete_by = created_at + timedelta(minutes=int(getattr(settings, "RIDE_COMPLETE_SLA_MIN", 60)))
    sla = {
        "assign_by": assign_by,
        "complete_by": complete_by,
        "created_at": created_at,
    }
    db = get_db()
    db.rides.update_one({"_id": ride_doc.get("_id")}, {"$set": {"sla": sla}})
    _schedule_ride_timeouts(str(ride_doc.get("_id")), assign_by, complete_by)
    return db.rides.find_one({"_id": ride_doc.get("_id")})


def _schedule_ride_timeouts(ride_id: str, assign_by, complete_by):
    try:
        assign_delay = max((assign_by - utcnow()).total_seconds(), 1)
        complete_delay = max((complete_by - utcnow()).total_seconds(), 1)
    except Exception:
        return
    timer_assign = threading.Timer(assign_delay, handle_ride_assign_timeout, args=(ride_id,))
    timer_assign.daemon = True
    timer_assign.start()
    timer_complete = threading.Timer(complete_delay, handle_ride_complete_timeout, args=(ride_id,))
    timer_complete.daemon = True
    timer_complete.start()


def handle_ride_assign_timeout(ride_id: str):
    db = get_db()
    oid = to_object_id(ride_id)
    if not oid:
        return
    ride = db.rides.find_one({"_id": oid})
    if not ride:
        return
    if ride.get("status") in {"COMPLETED", "CANCELLED", "FAILED"}:
        return
    if ride.get("status") in {"REQUESTED", "PENDING_PAYMENT"}:
        set_ride_status(ride_id, "CANCELLED", reason="ASSIGN_TIMEOUT")
        db.rides.update_one({"_id": oid}, {"$set": {"job_status": "NO_CAPTAIN"}})


def handle_ride_complete_timeout(ride_id: str):
    db = get_db()
    oid = to_object_id(ride_id)
    if not oid:
        return
    ride = db.rides.find_one({"_id": oid})
    if not ride:
        return
    if ride.get("status") in {"COMPLETED", "CANCELLED", "FAILED"}:
        return
    if ride.get("status") == "ASSIGNED":
        set_ride_status(ride_id, "CANCELLED", reason="COMPLETE_TIMEOUT")


def handle_no_captain(ride_id: str):
    db = get_db()
    oid = to_object_id(ride_id)
    if not oid:
        return False
    ride = db.rides.find_one({"_id": oid})
    if not ride:
        return False
    retries = int(ride.get("matching_retry_count", 0))
    max_retries = int(getattr(settings, "MATCH_RETRY_MAX", 2))
    if retries >= max_retries:
        try:
            set_ride_status(ride_id, "CANCELLED", reason="NO_CAPTAIN")
        except Exception:
            pass
        return False
    delay = int(getattr(settings, "MATCH_RETRY_DELAY_SEC", 20)) * (retries + 1)
    db.rides.update_one(
        {"_id": oid},
        {"$set": {"job_status": "RETRYING", "next_retry_at": utcnow() + timedelta(seconds=delay)}, "$inc": {"matching_retry_count": 1}},
    )

    def _retry():
        try:
            from core import matching_service
            matching_service.create_job("RIDE", ride_id)
        except Exception:
            pass

    timer = threading.Timer(delay, _retry)
    timer.daemon = True
    timer.start()
    return True
