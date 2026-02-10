from core.db import get_db
from core.utils import utcnow, to_object_id


def create_ticket(user_id: str, role: str, subject: str, message: str, category: str = None, priority: str = None):
    db = get_db()
    doc = {
        "user_id": to_object_id(user_id),
        "role": role,
        "subject": subject,
        "message": message,
        "category": category,
        "priority": priority or "NORMAL",
        "status": "OPEN",
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    result = db.support_tickets.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc
