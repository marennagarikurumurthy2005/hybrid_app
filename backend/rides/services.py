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
from core.vehicles import get_vehicle_rate, is_ev_vehicle
from rewards import services as reward_services
from vehicles import services as vehicle_services

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


def calculate_fare(pickup: dict, dropoff: dict, vehicle_type: str):
    distance_km = haversine_km(pickup["lat"], pickup["lng"], dropoff["lat"], dropoff["lng"])
    rate = get_vehicle_rate(vehicle_type)
    if rate is None:
        raise ValueError("Invalid vehicle type")
    return max(distance_km * rate, 0.0)


def create_ride(
    user_id: str,
    pickup: dict,
    dropoff: dict,
    vehicle_type: str,
    payment_mode: str,
    wallet_amount: Optional[int],
    redeem_points: Optional[int] = None,
):
    mode = normalize_payment_mode(payment_mode)
    if not mode:
        raise ValueError("Invalid payment mode")

    raw_base_fare = calculate_fare(pickup, dropoff, vehicle_type)
    surge_data = None
    surge_multiplier = 1.0
    try:
        surge_data = pricing_services.calculate_surge("RIDE", pickup["lat"], pickup["lng"])
        surge_multiplier = float(surge_data.get("surge_multiplier", 1.0))
    except Exception:
        surge_multiplier = 1.0
    base_fare = int(round(raw_base_fare))
    total_fare = int(round(raw_base_fare * surge_multiplier))
    surge_amount = max(0, total_fare - base_fare)
    is_ev = bool(is_ev_vehicle(vehicle_type))
    reward_multiplier = vehicle_services.get_ev_reward_percentage() * vehicle_services.get_ev_bonus_multiplier()
    reward_points_earned = int(total_fare * reward_multiplier) if is_ev else 0

    redeem_points_applied = 0
    redeem_amount = 0
    if redeem_points is not None:
        redeem_points_applied, redeem_amount, _ = reward_services.calculate_redeemable_points(
            user_id,
            total_fare,
            redeem_points,
        )
    total_after_rewards = max(0, total_fare - redeem_amount)
    wallet_to_use = 0
    if mode == "WALLET":
        wallet_to_use = int(wallet_amount or total_after_rewards)
        if wallet_to_use < total_after_rewards:
            raise ValueError("Wallet amount must cover the full fare")
        if wallet_to_use > total_after_rewards:
            wallet_to_use = total_after_rewards
    elif mode == "WALLET_RAZORPAY":
        wallet_to_use = int(wallet_amount or 0)
        if wallet_to_use < 0 or wallet_to_use > total_after_rewards:
            raise ValueError("Invalid wallet amount")

    payment_amount = total_after_rewards - wallet_to_use
    ride_id = ObjectId()
    wallet_txn = None
    reward_txn = None

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
        "vehicle_type": vehicle_type,
        "is_ev": is_ev,
        "reward_points_earned": reward_points_earned,
        "rewarded": False,
        "fare": total_fare,
        "fare_base": base_fare,
        "surge_multiplier": round(surge_multiplier, 2),
        "surge_amount": surge_amount,
        "surge_meta": surge_data,
        "wallet_amount": wallet_to_use,
        "reward_redeem_amount": redeem_amount,
        "points_redeemed": redeem_points_applied,
        "amount_total_before_rewards": total_fare,
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

        if redeem_points_applied > 0:
            reward_txn = reward_services.redeem_reward_points(
                user_id,
                redeem_points_applied,
                related_order=str(ride_id),
            )
            if not reward_txn:
                raise ValueError("Insufficient reward points")

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
        if reward_txn:
            reward_services.credit_reward_points(
                user_id,
                redeem_points_applied,
                "RIDE_REFUND",
                related_order=str(ride_id),
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
    ride_doc = db.rides.find_one({"_id": oid})
    if not ride_doc:
        return None
    db.rides.update_one({"_id": oid}, {"$set": {"status": "COMPLETED"}})
    if (
        ride_doc.get("is_ev")
        and not ride_doc.get("rewarded")
        and int(ride_doc.get("reward_points_earned") or 0) > 0
        and (ride_doc.get("is_paid") or ride_doc.get("payment_mode") == "COD")
    ):
        txn = reward_services.credit_reward_points(
            str(ride_doc.get("user_id")),
            int(ride_doc.get("reward_points_earned") or 0),
            reward_services.REWARD_SOURCE_EV_RIDE,
            related_order=str(ride_id),
        )
        db.rides.update_one({"_id": oid}, {"$set": {"rewarded": True}})
        if txn:
            try:
                notification_services.send_to_user(
                    str(ride_doc.get("user_id")),
                    "EV Rewards earned",
                    f"You earned {int(ride_doc.get('reward_points_earned') or 0)} reward points on your EV ride.",
                    {"ride_id": str(ride_id)},
                )
            except Exception:
                pass
    return db.rides.find_one({"_id": oid})
