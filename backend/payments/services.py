import razorpay
from django.conf import settings

from core.db import get_db
from core.utils import utcnow


_client = None


def get_client():
    global _client
    if _client is None:
        if not settings.RAZORPAY_KEY or not settings.RAZORPAY_SECRET:
            raise RuntimeError("Razorpay keys are not configured")
        _client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))
    return _client


def create_razorpay_order(amount: int, receipt: str, currency: str = "INR"):
    client = get_client()
    order = client.order.create({
        "amount": int(amount),
        "currency": currency,
        "receipt": receipt,
    })
    db = get_db()
    db.payment_transactions.insert_one({
        "provider": "RAZORPAY",
        "razorpay_order_id": order.get("id"),
        "amount": int(amount),
        "currency": currency,
        "status": order.get("status", "created"),
        "receipt": receipt,
        "created_at": utcnow(),
    })
    return order


def verify_razorpay_signature(razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str):
    client = get_client()
    client.utility.verify_payment_signature({
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    })
    db = get_db()
    db.payment_transactions.update_one(
        {"razorpay_order_id": razorpay_order_id},
        {"$set": {
            "razorpay_payment_id": razorpay_payment_id,
            "signature": razorpay_signature,
            "status": "paid",
            "paid_at": utcnow(),
        }},
        upsert=True,
    )
    return True
