import threading
from datetime import timedelta

from django.conf import settings
from pymongo import ReturnDocument

from core.db import get_db
from core.utils import utcnow, to_object_id

ORDER_STATUSES = {
    "PENDING_PAYMENT",
    "PLACED",
    "ASSIGNED",
    "DELIVERED",
    "CANCELLED",
    "FAILED",
}

ORDER_STATUS_TRANSITIONS = {
    "PENDING_PAYMENT": {"PLACED", "FAILED", "CANCELLED"},
    "PLACED": {"ASSIGNED", "CANCELLED"},
    "ASSIGNED": {"DELIVERED", "CANCELLED"},
    "DELIVERED": set(),
    "CANCELLED": set(),
    "FAILED": set(),
}


def _transition_allowed(current_status: str, new_status: str) -> bool:
    if not current_status:
        return True
    allowed = ORDER_STATUS_TRANSITIONS.get(current_status)
    if allowed is None:
        return True
    return new_status in allowed


def set_order_status(order_id: str, new_status: str, reason: str = None):
    if new_status not in ORDER_STATUSES:
        raise ValueError("Invalid order status")
    db = get_db()
    oid = to_object_id(order_id)
    if not oid:
        return None
    order = db.orders.find_one({"_id": oid})
    if not order:
        return None
    current = order.get("status")
    if current == new_status:
        return order
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
    return db.orders.find_one_and_update(
        {"_id": oid},
        {"$set": update, "$push": {"status_history": entry}},
        return_document=ReturnDocument.AFTER,
    )


def ensure_order_sla(order_doc: dict):
    if not order_doc:
        return None
    if order_doc.get("sla"):
        return order_doc
    created_at = order_doc.get("created_at") or utcnow()
    assign_by = created_at + timedelta(seconds=int(getattr(settings, "ORDER_ASSIGN_TIMEOUT_SEC", 600)))
    deliver_by = created_at + timedelta(minutes=int(getattr(settings, "ORDER_DELIVERY_SLA_MIN", 45)))
    sla = {
        "assign_by": assign_by,
        "deliver_by": deliver_by,
        "created_at": created_at,
    }
    db = get_db()
    db.orders.update_one({"_id": order_doc.get("_id")}, {"$set": {"sla": sla}})
    _schedule_order_timeouts(str(order_doc.get("_id")), assign_by, deliver_by)
    return db.orders.find_one({"_id": order_doc.get("_id")})


def _schedule_order_timeouts(order_id: str, assign_by, deliver_by):
    try:
        assign_delay = max((assign_by - utcnow()).total_seconds(), 1)
        deliver_delay = max((deliver_by - utcnow()).total_seconds(), 1)
    except Exception:
        return
    timer_assign = threading.Timer(assign_delay, handle_order_assign_timeout, args=(order_id,))
    timer_assign.daemon = True
    timer_assign.start()
    timer_deliver = threading.Timer(deliver_delay, handle_order_delivery_timeout, args=(order_id,))
    timer_deliver.daemon = True
    timer_deliver.start()


def handle_order_assign_timeout(order_id: str):
    db = get_db()
    oid = to_object_id(order_id)
    if not oid:
        return
    order = db.orders.find_one({"_id": oid})
    if not order:
        return
    if order.get("status") in {"DELIVERED", "CANCELLED", "FAILED"}:
        return
    if order.get("status") in {"PLACED", "PENDING_PAYMENT"}:
        set_order_status(order_id, "CANCELLED", reason="ASSIGN_TIMEOUT")
        db.orders.update_one({"_id": oid}, {"$set": {"job_status": "NO_CAPTAIN"}})


def handle_order_delivery_timeout(order_id: str):
    db = get_db()
    oid = to_object_id(order_id)
    if not oid:
        return
    order = db.orders.find_one({"_id": oid})
    if not order:
        return
    if order.get("status") in {"DELIVERED", "CANCELLED", "FAILED"}:
        return
    if order.get("status") == "ASSIGNED":
        set_order_status(order_id, "CANCELLED", reason="DELIVERY_TIMEOUT")


def handle_no_captain(order_id: str):
    db = get_db()
    oid = to_object_id(order_id)
    if not oid:
        return False
    order = db.orders.find_one({"_id": oid})
    if not order:
        return False
    retries = int(order.get("matching_retry_count", 0))
    max_retries = int(getattr(settings, "MATCH_RETRY_MAX", 2))
    if retries >= max_retries:
        try:
            set_order_status(order_id, "CANCELLED", reason="NO_CAPTAIN")
        except Exception:
            pass
        return False
    delay = int(getattr(settings, "MATCH_RETRY_DELAY_SEC", 20)) * (retries + 1)
    db.orders.update_one(
        {"_id": oid},
        {"$set": {"job_status": "RETRYING", "next_retry_at": utcnow() + timedelta(seconds=delay)}, "$inc": {"matching_retry_count": 1}},
    )

    def _retry():
        try:
            from core import matching_service
            matching_service.create_job("ORDER", order_id)
        except Exception:
            pass

    timer = threading.Timer(delay, _retry)
    timer.daemon = True
    timer.start()
    return True
