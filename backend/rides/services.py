import math
from typing import Optional
from bson import ObjectId
from core.db import get_db
from core.utils import utcnow, to_object_id
from core.geo_utils import to_point
from wallet import services as wallet_services
from payments import services as payment_services
from notifications import services as notification_services
from core import matching_service
from pricing import services as pricing_services

PAYMENT_MODES = {"RAZORPAY", "WALLET", "WALLET_RAZORPAY"}


def normalize_payment_mode(mode: Optional[str]):
    if not mode:
        return None
    cleaned = mode.upper().replace(" ", "")
    if cleaned in {"WALLET+RAZORPAY", "WALLET&RAZORPAY", "WALLET_RAZORPAY"}:
        return "WALLET_RAZORPAY"
    if cleaned in {"RAZORPAY", "WALLET"}:
        return cleaned
    return None


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def calculate_fare(pickup: dict, dropoff: dict):
    distance_km = haversine_km(pickup["lat"], pickup["lng"], dropoff["lat"], dropoff["lng"])
    base_fare = 3000
    per_km = 1500
    fare = base_fare + int(distance_km * per_km)
    return max(fare, base_fare)


def create_ride(user_id: str, pickup: dict, dropoff: dict, payment_mode: str, wallet_amount: Optional[int]):
    mode = normalize_payment_mode(payment_mode)
    if not mode:
        raise ValueError("Invalid payment mode")

    base_fare = calculate_fare(pickup, dropoff)
    surge_data = None
    surge_multiplier = 1.0
    try:
        surge_data = pricing_services.calculate_surge("RIDE", pickup["lat"], pickup["lng"])
        surge_multiplier = float(surge_data.get("surge_multiplier", 1.0))
    except Exception:
        surge_multiplier = 1.0
    fare = pricing_services.apply_surge(base_fare, surge_multiplier)
    surge_amount = max(0, fare - base_fare)
    wallet_to_use = 0
    if mode == "WALLET":
        wallet_to_use = int(wallet_amount or fare)
        if wallet_to_use < fare:
            raise ValueError("Wallet amount must cover the full fare")
    elif mode == "WALLET_RAZORPAY":
        wallet_to_use = int(wallet_amount or 0)
        if wallet_to_use < 0 or wallet_to_use > fare:
            raise ValueError("Invalid wallet amount")

    payment_amount = fare - wallet_to_use
    ride_id = ObjectId()
    wallet_txn = None

    if wallet_to_use > 0:
        wallet_txn = wallet_services.debit_wallet(
            user_id,
            wallet_to_use,
            "RIDE_PAYMENT",
            "RIDE",
            reference=str(ride_id),
        )
        if not wallet_txn:
            raise ValueError("Insufficient wallet balance")

    pickup_location = to_point(pickup["lat"], pickup["lng"])
    ride_doc = {
        "_id": ride_id,
        "user_id": to_object_id(user_id),
        "pickup": pickup,
        "dropoff": dropoff,
        "pickup_location": pickup_location,
        "fare": fare,
        "fare_base": base_fare,
        "surge_multiplier": round(surge_multiplier, 2),
        "surge_amount": surge_amount,
        "surge_meta": surge_data,
        "wallet_amount": wallet_to_use,
        "payment_amount": payment_amount,
        "payment_mode": mode,
        "status": "REQUESTED" if payment_amount == 0 else "PENDING_PAYMENT",
        "is_paid": payment_amount == 0,
        "job_status": "CREATED",
        "current_offer": None,
        "job_attempts": 0,
        "rejected_captains": [],
        "created_at": utcnow(),
        "captain_id": None,
    }

    db = get_db()
    try:
        db.rides.insert_one(ride_doc)
        razorpay_order = None
        if payment_amount > 0 and mode in {"RAZORPAY", "WALLET_RAZORPAY"}:
            razorpay_order = payment_services.create_razorpay_order(
                amount=payment_amount,
                receipt=f"ride_{ride_id}",
            )
            db.rides.update_one(
                {"_id": ride_id},
                {"$set": {"razorpay_order_id": razorpay_order.get("id")}},
            )

        notification_services.send_to_user(
            user_id,
            "Ride created",
            "Your ride request has been placed.",
            {"ride_id": str(ride_id)},
        )

        try:
            matching_service.create_job("RIDE", str(ride_id))
        except Exception:
            db.rides.update_one(
                {"_id": ride_id},
                {"$set": {"job_status": "MATCHING_FAILED"}},
            )

        ride_doc = db.rides.find_one({"_id": ride_id})
        return ride_doc, razorpay_order
    except Exception as exc:
        db.rides.update_one({"_id": ride_id}, {"$set": {"status": "FAILED"}})
        if wallet_txn:
            wallet_services.refund_wallet(
                user_id,
                wallet_to_use,
                "RIDE_FAILED",
                "RIDE",
                reference=str(ride_id),
            )
        raise exc


def verify_ride_payment(ride_id: str, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str):
    db = get_db()
    oid = to_object_id(ride_id)
    if not oid:
        raise ValueError("Invalid ride id")

    payment_services.verify_razorpay_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature)

    result = db.rides.update_one(
        {"_id": oid},
        {"$set": {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
            "is_paid": True,
            "status": "REQUESTED",
        }},
    )
    if result.matched_count == 0:
        raise ValueError("Ride not found")
    return db.rides.find_one({"_id": oid})


def complete_ride(ride_id: str):
    db = get_db()
    oid = to_object_id(ride_id)
    if not oid:
        return None
    db.rides.update_one({"_id": oid}, {"$set": {"status": "COMPLETED"}})
    return db.rides.find_one({"_id": oid})
