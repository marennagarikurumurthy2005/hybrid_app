from typing import Optional, Dict
import json
from datetime import datetime, timezone

from firebase_admin import messaging
from django.conf import settings
from pymongo import ReturnDocument

from core.firebase import get_firebase_app
from core.db import get_db
from core.utils import to_object_id, utcnow
from core.redis_queue import get_client

_index_ready = False


def ensure_indexes():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.notifications.create_index([("created_at", -1)], name="notifications_created_at")
    db.notifications.create_index([("status", 1), ("send_at", 1)], name="notifications_status_send_at")
    db.notification_logs.create_index([("created_at", -1)], name="notification_logs_created_at")
    db.notification_receipts.create_index([("notification_id", 1), ("created_at", -1)], name="notification_receipts_id")
    _index_ready = True


def _priority_queue(priority: str) -> str:
    value = (priority or "NORMAL").upper()
    if value == "HIGH":
        return "notifications:queue:high"
    if value == "LOW":
        return "notifications:queue:low"
    return "notifications:queue:normal"


def send_notification(token: str, title: str, body: str, data: Optional[Dict] = None, silent: bool = False, priority: str = "NORMAL"):
    if not token:
        return False
    try:
        get_firebase_app()
        message = messaging.Message(
            token=token,
            notification=None if silent else messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in (data or {}).items()},
            android=messaging.AndroidConfig(priority=priority.lower()),
        )
        messaging.send(message)
        return True
    except Exception:
        return False


def send_to_user(user_id: str, title: str, body: str, data: Optional[Dict] = None, silent: bool = False, priority: str = "NORMAL"):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return False
    user_doc = db.users.find_one({"_id": oid})
    if not user_doc or not user_doc.get("fcm_token"):
        return False
    return send_notification(user_doc["fcm_token"], title, body, data, silent=silent, priority=priority)


def enqueue_notification(payload: dict):
    ensure_indexes()
    db = get_db()
    payload["status"] = payload.get("status") or "QUEUED"
    payload["retry_count"] = int(payload.get("retry_count", 0))
    payload["created_at"] = utcnow()
    result = db.notifications.insert_one(payload)
    payload["_id"] = result.inserted_id

    client = get_client()
    client.rpush(
        _priority_queue(payload.get("priority")),
        json.dumps({"notification_id": str(payload["_id"])}, default=str),
    )
    return payload


def queue_notification_id(notification_id: str):
    ensure_indexes()
    db = get_db()
    notif = db.notifications.find_one_and_update(
        {"_id": to_object_id(notification_id)},
        {"$set": {"status": "QUEUED"}},
        return_document=ReturnDocument.AFTER,
    )
    if not notif:
        return False
    client = get_client()
    priority = notif.get("priority") if notif else "NORMAL"
    client.rpush(_priority_queue(priority), json.dumps({"notification_id": str(notification_id)}, default=str))
    return True


def schedule_notification(payload: dict, send_at: datetime):
    ensure_indexes()
    db = get_db()
    payload["status"] = "SCHEDULED"
    payload["created_at"] = utcnow()
    payload["send_at"] = send_at
    result = db.notifications.insert_one(payload)
    payload["_id"] = result.inserted_id

    client = get_client()
    score = send_at.replace(tzinfo=timezone.utc).timestamp()
    client.zadd("notifications:schedule", {str(payload["_id"]): score})
    return payload


def _log_notification(notification_id: str, status: str, detail: Optional[str] = None):
    db = get_db()
    db.notification_logs.insert_one({
        "notification_id": to_object_id(notification_id),
        "status": status,
        "detail": detail,
        "created_at": utcnow(),
    })


def _log_receipt(notification_id: str, status: str, detail: Optional[str] = None):
    db = get_db()
    db.notification_receipts.insert_one({
        "notification_id": to_object_id(notification_id),
        "status": status,
        "detail": detail,
        "created_at": utcnow(),
    })


def process_queue(max_items: int = 50):
    client = get_client()
    db = get_db()
    processed = 0
    for _ in range(max_items):
        raw = client.lpop("notifications:queue:high")
        if not raw:
            raw = client.lpop("notifications:queue:normal")
        if not raw:
            raw = client.lpop("notifications:queue:low")
        if not raw:
            break
        processed += 1
        data = json.loads(raw)
        notification_id = data.get("notification_id")
        if not notification_id:
            continue
        notif = db.notifications.find_one({"_id": to_object_id(notification_id)})
        if not notif:
            continue
        success = False
        if notif.get("topic"):
            try:
                get_firebase_app()
                message = messaging.Message(
                    topic=notif.get("topic"),
                    notification=None if notif.get("silent") else messaging.Notification(
                        title=notif.get("title"), body=notif.get("body")
                    ),
                    data={k: str(v) for k, v in (notif.get("data") or {}).items()},
                )
                messaging.send(message)
                success = True
            except Exception as exc:
                success = False
                _log_notification(notification_id, "FAILED", str(exc))
        else:
            if not notif.get("user_id"):
                success = False
            else:
                success = send_to_user(
                    str(notif.get("user_id")),
                    notif.get("title"),
                    notif.get("body"),
                    notif.get("data"),
                    silent=bool(notif.get("silent")),
                    priority=notif.get("priority") or "NORMAL",
                )
        if success:
            db.notifications.update_one(
                {"_id": notif.get("_id")},
                {"$set": {"status": "SENT", "sent_at": utcnow()}},
            )
            _log_notification(notification_id, "SENT")
            _log_receipt(notification_id, "SENT")
        else:
            retries = int(notif.get("retry_count", 0)) + 1
            if retries <= settings.NOTIFICATION_MAX_RETRIES:
                db.notifications.update_one(
                    {"_id": notif.get("_id")},
                    {"$set": {"status": "QUEUED"}, "$inc": {"retry_count": 1}},
                )
                client.rpush(
                    _priority_queue(notif.get("priority")),
                    json.dumps({"notification_id": str(notification_id)}, default=str),
                )
            else:
                db.notifications.update_one(
                    {"_id": notif.get("_id")},
                    {"$set": {"status": "FAILED", "sent_at": utcnow()}, "$inc": {"retry_count": 1}},
                )
            _log_notification(notification_id, "FAILED")
            _log_receipt(notification_id, "FAILED")
    return processed


def dispatch_scheduled(max_items: int = 50):
    client = get_client()
    now_ts = datetime.now(timezone.utc).timestamp()
    ids = client.zrangebyscore("notifications:schedule", 0, now_ts, start=0, num=max_items)
    if not ids:
        return 0
    for notif_id in ids:
        client.zrem("notifications:schedule", notif_id)
        queue_notification_id(notif_id)
    return len(ids)


def list_notifications(user_id: Optional[str] = None, limit: int = 50):
    db = get_db()
    query = {}
    if user_id:
        query["user_id"] = to_object_id(user_id)
    cursor = db.notifications.find(query).sort("created_at", -1).limit(limit)
    return list(cursor)
