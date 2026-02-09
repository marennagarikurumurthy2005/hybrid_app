from typing import Optional, Dict
from firebase_admin import messaging
from core.firebase import get_firebase_app
from core.db import get_db
from core.utils import to_object_id


def send_notification(token: str, title: str, body: str, data: Optional[Dict] = None):
    if not token:
        return False
    try:
        get_firebase_app()
        message = messaging.Message(
            token=token,
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in (data or {}).items()},
        )
        messaging.send(message)
        return True
    except Exception:
        return False


def send_to_user(user_id: str, title: str, body: str, data: Optional[Dict] = None):
    db = get_db()
    oid = to_object_id(user_id)
    if not oid:
        return False
    user_doc = db.users.find_one({"_id": oid})
    if not user_doc or not user_doc.get("fcm_token"):
        return False
    return send_notification(user_doc["fcm_token"], title, body, data)
