from core.db import get_db
from core.utils import utcnow, to_object_id


def get_user_by_phone(phone: str):
    db = get_db()
    return db.users.find_one({"phone": phone})


def get_user_by_id(user_id: str):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    return db.users.find_one({"_id": oid})


def create_user(phone: str, role: str):
    db = get_db()
    doc = {
        "phone": phone,
        "role": role,
        "wallet_balance": 0,
        "is_active": True,
        "created_at": utcnow(),
        "fcm_token": None,
    }
    result = db.users.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def set_fcm_token(user_id: str, fcm_token: str):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    db.users.update_one({"_id": oid}, {"$set": {"fcm_token": fcm_token}})
    return db.users.find_one({"_id": oid})


def update_role(user_id: str, role: str):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return None
    db.users.update_one({"_id": oid}, {"$set": {"role": role}})
    return db.users.find_one({"_id": oid})
