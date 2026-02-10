import re
from typing import Optional, List

from django.conf import settings
from core.db import get_db
from core.utils import utcnow, to_object_id

_index_ready = False


def ensure_indexes():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.chats.create_index([("room_id", 1)], unique=True, name="chats_room_id")
    db.messages.create_index([("room_id", 1), ("created_at", -1)], name="messages_room_created_at")
    _index_ready = True


def _abuse_words():
    words = getattr(settings, "CHAT_ABUSE_WORDS", None)
    if words:
        return [w.strip().lower() for w in words if w.strip()]
    return ["abuse", "spam"]


def filter_message(text: str) -> str:
    cleaned = text or ""
    for word in _abuse_words():
        if not word:
            continue
        cleaned = re.sub(rf"\b{re.escape(word)}\b", "***", cleaned, flags=re.IGNORECASE)
    return cleaned


def ensure_chat_room(room_id: str, participants: Optional[List[dict]] = None, job_type: Optional[str] = None):
    ensure_indexes()
    db = get_db()
    doc = db.chats.find_one({"room_id": room_id})
    if doc:
        return doc
    doc = {
        "room_id": room_id,
        "participants": participants or [],
        "job_type": job_type,
        "created_at": utcnow(),
        "last_message_at": None,
    }
    db.chats.insert_one(doc)
    return doc


def store_message(
    room_id: str,
    sender_id: str,
    sender_role: str,
    receiver_id: Optional[str],
    receiver_role: Optional[str],
    text: str,
    client_message_id: Optional[str] = None,
):
    ensure_indexes()
    db = get_db()
    clean_text = filter_message(text)
    doc = {
        "room_id": room_id,
        "sender_id": to_object_id(sender_id),
        "sender_role": sender_role,
        "receiver_id": to_object_id(receiver_id) if receiver_id else None,
        "receiver_role": receiver_role,
        "text": clean_text,
        "client_message_id": client_message_id,
        "created_at": utcnow(),
        "delivered_to": [],
    }
    result = db.messages.insert_one(doc)
    doc["_id"] = result.inserted_id
    db.chats.update_one({"room_id": room_id}, {"$set": {"last_message_at": utcnow()}}, upsert=True)
    return doc


def list_messages(room_id: str, limit: int = 50):
    ensure_indexes()
    db = get_db()
    cursor = db.messages.find({"room_id": room_id}).sort("created_at", -1).limit(limit)
    return list(cursor)


def mark_delivered(message_id: str, user_id: str):
    ensure_indexes()
    db = get_db()
    oid = to_object_id(message_id)
    if not oid:
        return None
    result = db.messages.update_one(
        {"_id": oid},
        {"$addToSet": {"delivered_to": to_object_id(user_id)}, "$set": {"delivered_at": utcnow()}},
    )
    if result.matched_count == 0:
        return None
    return db.messages.find_one({"_id": oid})


def get_masked_numbers(room_id: str, caller_id: str, callee_id: str):
    salt = f"{room_id}:{caller_id}:{callee_id}".encode("utf-8")
    digest = re.sub(r"\\D", "", str(int.from_bytes(salt, "big")))
    if not digest:
        digest = "1234567890"
    masked = int(digest[-10:])
    caller_proxy = f"9{masked:09d}"[-10:]
    callee_proxy = f"8{masked:09d}"[-10:]
    return {
        "caller_proxy": caller_proxy,
        "callee_proxy": callee_proxy,
        "expires_in_min": 30,
    }


def is_participant(room_id: str, user_id: str, role: str) -> bool:
    db = get_db()
    oid = to_object_id(room_id)
    if not oid:
        return False
    role = (role or "").upper()
    order = db.orders.find_one({"_id": oid})
    if order:
        if role == "USER" and str(order.get("user_id")) == str(user_id):
            return True
        if role == "CAPTAIN" and str(order.get("captain_id")) == str(user_id):
            return True
        if role == "RESTAURANT":
            restaurant = db.restaurants.find_one({"_id": order.get("restaurant_id")})
            if restaurant and str(restaurant.get("owner_id")) == str(to_object_id(user_id)):
                return True
        return False
    ride = db.rides.find_one({"_id": oid})
    if ride:
        if role == "USER" and str(ride.get("user_id")) == str(user_id):
            return True
        if role == "CAPTAIN" and str(ride.get("captain_id")) == str(user_id):
            return True
        return False
    return False
