from typing import Optional
from datetime import datetime, timezone
from pymongo import ReturnDocument, ASCENDING

from core.db import get_db
from core.utils import utcnow, to_object_id
from rewards import services as reward_services

_index_ready = False


def ensure_indexes():
    global _index_ready
    if _index_ready:
        return
    db = get_db()
    db.coupons.create_index([("code", ASCENDING)], unique=True, name="coupons_code")
    db.coupons.create_index([("expires_at", ASCENDING)], name="coupons_expires")
    db.campaigns.create_index([("active", ASCENDING), ("starts_at", ASCENDING)], name="campaigns_active")
    db.referrals.create_index([("referral_code", ASCENDING)], unique=True, name="referrals_code")
    _index_ready = True


def _is_expired(expires_at) -> bool:
    if not expires_at:
        return False
    if isinstance(expires_at, datetime):
        return expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc)
    return False


def apply_coupon(user_id: str, code: str, amount: int, job_type: str):
    ensure_indexes()
    db = get_db()
    coupon = db.coupons.find_one({"code": (code or "").upper(), "active": True})
    if not coupon:
        raise ValueError("Coupon not found")
    if _is_expired(coupon.get("expires_at")):
        raise ValueError("Coupon expired")
    usage_limit = coupon.get("usage_limit")
    if usage_limit is not None and int(coupon.get("used_count", 0)) >= int(usage_limit):
        raise ValueError("Coupon usage limit reached")
    if int(amount) < int(coupon.get("min_amount", 0)):
        raise ValueError("Order amount too low")
    if coupon.get("job_type") and coupon.get("job_type") != job_type:
        raise ValueError("Coupon not valid for this job type")

    discount = 0
    if coupon.get("type") == "PERCENT":
        discount = int(round(int(amount) * float(coupon.get("value", 0)) / 100.0))
    else:
        discount = int(coupon.get("value", 0))
    if coupon.get("max_discount"):
        discount = min(discount, int(coupon.get("max_discount")))
    discount = max(0, min(discount, int(amount)))

    effective_limit = int(usage_limit) if usage_limit is not None else 10**9
    updated = db.coupons.find_one_and_update(
        {"_id": coupon.get("_id"), "used_count": {"$lt": effective_limit}},
        {"$inc": {"used_count": 1}},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise ValueError("Coupon usage limit reached")

    db.coupon_redemptions.insert_one({
        "user_id": to_object_id(user_id),
        "coupon_id": coupon.get("_id"),
        "code": coupon.get("code"),
        "job_type": job_type,
        "amount": int(amount),
        "discount": discount,
        "created_at": utcnow(),
    })

    return {
        "code": coupon.get("code"),
        "discount": discount,
        "amount": int(amount),
        "payable": int(amount) - discount,
    }


def use_referral(user_id: str, referral_code: str):
    ensure_indexes()
    db = get_db()
    referral = db.referrals.find_one({"referral_code": referral_code})
    if not referral:
        raise ValueError("Invalid referral code")
    if db.referral_uses.find_one({"user_id": to_object_id(user_id), "referral_code": referral_code}):
        raise ValueError("Referral already used")

    db.referral_uses.insert_one({
        "user_id": to_object_id(user_id),
        "referral_code": referral_code,
        "created_at": utcnow(),
    })

    reward_services.credit_reward_points(user_id, int(referral.get("reward_points", 0)), "REFERRAL", related_order=None)
    referrer_id = referral.get("user_id")
    if referrer_id:
        reward_services.credit_reward_points(str(referrer_id), int(referral.get("referrer_points", 0)), "REFERRAL", related_order=None)

    return True


def list_active_campaigns(limit: int = 50):
    ensure_indexes()
    db = get_db()
    now = utcnow()
    cursor = db.campaigns.find({
        "active": True,
        "starts_at": {"$lte": now},
        "$or": [{"ends_at": None}, {"ends_at": {"$gte": now}}],
    }).sort("starts_at", -1).limit(limit)
    return list(cursor)
