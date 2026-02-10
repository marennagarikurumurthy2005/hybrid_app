from typing import Optional, Dict

from core.db import get_db
from core.utils import utcnow, to_object_id
from wallet import services as wallet_services
from payments import services as payment_services
from notifications import services as notification_services
from payouts import services as payout_services


DEFAULT_POLICY = {
    "user_cancel_before_assign_refund_pct": 1.0,
    "user_cancel_after_assign_refund_pct": 0.5,
    "captain_cancel_penalty_pct": 0.1,
    "late_delivery_refund_pct": 0.2,
    "no_show_fee_pct": 0.1,
}

_index_ready = False


def ensure_indexes():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.cancellations.create_index([("created_at", -1)], name="cancellations_created_at")
    db.cancellations.create_index([("job_type", 1), ("job_id", 1)], name="cancellations_job")
    db.penalties.create_index([("created_at", -1)], name="penalties_created_at")
    db.refunds.create_index([("created_at", -1)], name="refunds_created_at")
    _index_ready = True


def get_policy():
    return DEFAULT_POLICY.copy()


def _calculate_pct_amount(amount: int, pct: float) -> int:
    return int(round(max(amount, 0) * max(pct, 0.0)))


def _create_refund_doc(user_id: str, amount: int, source: str, reference: str, method: str, meta: Optional[Dict] = None):
    if amount <= 0:
        return None
    db = get_db()
    doc = {
        "user_id": to_object_id(user_id),
        "amount": int(amount),
        "source": source,
        "reference": reference,
        "method": method,
        "meta": meta or {},
        "created_at": utcnow(),
    }
    db.refunds.insert_one(doc)
    return doc


def _create_penalty_doc(actor_id: str, amount: int, reason: str, reference: str, meta: Optional[Dict] = None):
    if amount <= 0:
        return None
    db = get_db()
    doc = {
        "actor_id": to_object_id(actor_id),
        "amount": int(amount),
        "reason": reason,
        "reference": reference,
        "meta": meta or {},
        "created_at": utcnow(),
    }
    db.penalties.insert_one(doc)
    return doc


def _apply_refund(user_id: str, amount: int, reference: str, payment_mode: str, razorpay_payment_id: Optional[str]):
    if amount <= 0:
        return None
    method = "WALLET"
    if payment_mode in {"RAZORPAY", "WALLET_RAZORPAY"} and razorpay_payment_id:
        try:
            payment_services.refund_razorpay_payment(razorpay_payment_id, amount)
            method = "RAZORPAY"
        except Exception:
            method = "WALLET"
    if method == "WALLET":
        wallet_services.credit_wallet(user_id, amount, "CANCEL_REFUND", "REFUND", reference=reference)
    return _create_refund_doc(user_id, amount, "CANCEL", reference, method)


def _free_captain(captain_oid):
    if not captain_oid:
        return
    db = get_db()
    db.captains.update_one(
        {"user_id": captain_oid},
        {"$set": {"is_busy": False, "current_job_id": None, "current_job_type": None, "current_job": None}},
    )


def cancel_order(
    actor_id: str,
    order_id: str,
    actor_role: str,
    reason: str,
    late_delivery: bool = False,
    no_show: bool = False,
    metadata: Optional[Dict] = None,
):
    ensure_indexes()
    db = get_db()
    oid = to_object_id(order_id)
    if not oid:
        raise ValueError("Invalid order id")
    order = db.orders.find_one({"_id": oid})
    if not order:
        raise ValueError("Order not found")
    if order.get("status") in {"CANCELLED", "COMPLETED", "DELIVERED"}:
        raise ValueError("Order already closed")

    actor_role = (actor_role or "SYSTEM").upper()
    payment_mode = order.get("payment_mode")
    amount_paid = int(order.get("amount_total", 0))

    refund_amount = 0
    penalty_amount = 0

    if actor_role == "USER":
        if not order.get("captain_id"):
            refund_amount = _calculate_pct_amount(amount_paid, DEFAULT_POLICY["user_cancel_before_assign_refund_pct"])
        else:
            refund_amount = _calculate_pct_amount(amount_paid, DEFAULT_POLICY["user_cancel_after_assign_refund_pct"])
    elif actor_role == "CAPTAIN":
        refund_amount = amount_paid
        penalty_amount = _calculate_pct_amount(amount_paid, DEFAULT_POLICY["captain_cancel_penalty_pct"])
    elif actor_role == "RESTAURANT":
        refund_amount = amount_paid
    else:
        refund_amount = amount_paid

    if late_delivery:
        refund_amount = max(refund_amount, _calculate_pct_amount(amount_paid, DEFAULT_POLICY["late_delivery_refund_pct"]))

    if no_show:
        no_show_fee = _calculate_pct_amount(amount_paid, DEFAULT_POLICY["no_show_fee_pct"])
        if no_show_fee > 0:
            debited = wallet_services.debit_wallet(str(order.get("user_id")), no_show_fee, "NO_SHOW_FEE", "FOOD", reference=order_id)
            if not debited:
                _create_penalty_doc(str(order.get("user_id")), no_show_fee, "NO_SHOW_FEE", order_id, meta=metadata)
        refund_amount = 0

    cancellation_doc = {
        "job_type": "ORDER",
        "job_id": oid,
        "actor_id": to_object_id(actor_id),
        "actor_role": actor_role,
        "reason": reason,
        "late_delivery": bool(late_delivery),
        "no_show": bool(no_show),
        "metadata": metadata or {},
        "created_at": utcnow(),
    }
    db.cancellations.insert_one(cancellation_doc)

    db.orders.update_one(
        {"_id": oid},
        {"$set": {
            "status": "CANCELLED",
            "job_status": "CANCELLED",
            "cancelled_at": utcnow(),
            "cancelled_by": actor_role,
            "cancel_reason": reason,
            "current_offer": None,
        }},
    )

    captain_id = order.get("captain_id")
    if captain_id:
        _free_captain(captain_id)

    refund_doc = None
    if refund_amount > 0 and order.get("is_paid"):
        refund_doc = _apply_refund(
            str(order.get("user_id")),
            refund_amount,
            order_id,
            payment_mode,
            order.get("razorpay_payment_id"),
        )

    penalty_doc = None
    if penalty_amount > 0 and actor_role == "CAPTAIN" and captain_id:
        penalty_doc = _create_penalty_doc(str(captain_id), penalty_amount, "CAPTAIN_CANCEL", order_id, meta=metadata)
        payout_services.debit_wallet(str(captain_id), penalty_amount, "CAPTAIN_CANCEL", order_id)
        db.captains.update_one(
            {"user_id": captain_id},
            {"$inc": {"average_rating": -0.1}},
        )

    user_id = order.get("user_id")
    if user_id:
        notification_services.send_to_user(
            str(user_id),
            "Order cancelled",
            f"Your order {order_id} has been cancelled.",
            {"order_id": order_id, "reason": reason},
        )

    return {
        "cancellation": cancellation_doc,
        "refund": refund_doc,
        "penalty": penalty_doc,
    }


def cancel_ride(
    actor_id: str,
    ride_id: str,
    actor_role: str,
    reason: str,
    no_show: bool = False,
    metadata: Optional[Dict] = None,
):
    ensure_indexes()
    db = get_db()
    oid = to_object_id(ride_id)
    if not oid:
        raise ValueError("Invalid ride id")
    ride = db.rides.find_one({"_id": oid})
    if not ride:
        raise ValueError("Ride not found")
    if ride.get("status") in {"CANCELLED", "COMPLETED"}:
        raise ValueError("Ride already closed")

    actor_role = (actor_role or "SYSTEM").upper()
    payment_mode = ride.get("payment_mode")
    amount_paid = int(ride.get("fare", 0))

    refund_amount = 0
    penalty_amount = 0

    if actor_role == "USER":
        if not ride.get("captain_id"):
            refund_amount = _calculate_pct_amount(amount_paid, DEFAULT_POLICY["user_cancel_before_assign_refund_pct"])
        else:
            refund_amount = _calculate_pct_amount(amount_paid, DEFAULT_POLICY["user_cancel_after_assign_refund_pct"])
    elif actor_role == "CAPTAIN":
        refund_amount = amount_paid
        penalty_amount = _calculate_pct_amount(amount_paid, DEFAULT_POLICY["captain_cancel_penalty_pct"])
    else:
        refund_amount = amount_paid

    if no_show:
        no_show_fee = _calculate_pct_amount(amount_paid, DEFAULT_POLICY["no_show_fee_pct"])
        if no_show_fee > 0:
            debited = wallet_services.debit_wallet(str(ride.get("user_id")), no_show_fee, "NO_SHOW_FEE", "RIDE", reference=ride_id)
            if not debited:
                _create_penalty_doc(str(ride.get("user_id")), no_show_fee, "NO_SHOW_FEE", ride_id, meta=metadata)
        refund_amount = 0

    cancellation_doc = {
        "job_type": "RIDE",
        "job_id": oid,
        "actor_id": to_object_id(actor_id),
        "actor_role": actor_role,
        "reason": reason,
        "no_show": bool(no_show),
        "metadata": metadata or {},
        "created_at": utcnow(),
    }
    db.cancellations.insert_one(cancellation_doc)

    db.rides.update_one(
        {"_id": oid},
        {"$set": {
            "status": "CANCELLED",
            "job_status": "CANCELLED",
            "cancelled_at": utcnow(),
            "cancelled_by": actor_role,
            "cancel_reason": reason,
            "current_offer": None,
        }},
    )

    captain_id = ride.get("captain_id")
    if captain_id:
        _free_captain(captain_id)

    refund_doc = None
    if refund_amount > 0 and ride.get("is_paid"):
        refund_doc = _apply_refund(
            str(ride.get("user_id")),
            refund_amount,
            ride_id,
            payment_mode,
            ride.get("razorpay_payment_id"),
        )

    penalty_doc = None
    if penalty_amount > 0 and actor_role == "CAPTAIN" and captain_id:
        penalty_doc = _create_penalty_doc(str(captain_id), penalty_amount, "CAPTAIN_CANCEL", ride_id, meta=metadata)
        payout_services.debit_wallet(str(captain_id), penalty_amount, "CAPTAIN_CANCEL", ride_id)
        db.captains.update_one(
            {"user_id": captain_id},
            {"$inc": {"average_rating": -0.1}},
        )

    user_id = ride.get("user_id")
    if user_id:
        notification_services.send_to_user(
            str(user_id),
            "Ride cancelled",
            f"Your ride {ride_id} has been cancelled.",
            {"ride_id": ride_id, "reason": reason},
        )

    return {
        "cancellation": cancellation_doc,
        "refund": refund_doc,
        "penalty": penalty_doc,
    }
