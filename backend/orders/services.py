from typing import Optional, List, Dict
from bson import ObjectId
from core.db import get_db
from core.utils import utcnow, to_object_id
from wallet import services as wallet_services
from payments import services as payment_services
from notifications import services as notification_services
from core import matching_service
from pricing import services as pricing_services
from rewards import services as reward_services

PAYMENT_MODES = {"RAZORPAY", "COD", "WALLET", "WALLET_RAZORPAY"}


def normalize_payment_mode(mode: Optional[str]):
    if not mode:
        return None
    cleaned = mode.upper().replace(" ", "")
    if cleaned in {"WALLET+RAZORPAY", "WALLET&RAZORPAY", "WALLET_RAZORPAY"}:
        return "WALLET_RAZORPAY"
    if cleaned in {"RAZORPAY", "COD", "WALLET"}:
        return cleaned
    return None


def calculate_food_totals(restaurant_id: str, items: List[Dict]):
    db = get_db()
    rid = to_object_id(restaurant_id)
    if not rid:
        raise ValueError("Invalid restaurant id")
    if not items:
        raise ValueError("Items are required")

    item_ids = []
    quantities = {}
    for item in items:
        oid = to_object_id(item.get("menu_item_id"))
        qty = int(item.get("quantity", 0))
        if not oid or qty <= 0:
            raise ValueError("Invalid item or quantity")
        item_ids.append(oid)
        quantities[str(oid)] = quantities.get(str(oid), 0) + qty

    unique_ids = list({str(oid): oid for oid in item_ids}.values())
    menu_items = list(db.menu_items.find({"_id": {"$in": unique_ids}, "restaurant_id": rid, "is_available": True}))
    if len(menu_items) != len(unique_ids):
        raise ValueError("Some menu items are unavailable")

    subtotal = 0
    normalized_items = []
    for menu in menu_items:
        qty = quantities[str(menu["_id"])]
        line_total = int(menu["price"]) * qty
        subtotal += line_total
        normalized_items.append({
            "menu_item_id": menu["_id"],
            "name": menu.get("name"),
            "price": int(menu["price"]),
            "quantity": qty,
            "total": line_total,
        })

    return normalized_items, subtotal


def calculate_recommended_reward_points(restaurant_id: str, order_items: List[Dict], surge_multiplier: float):
    if not order_items:
        return 0
    db = get_db()
    rid = to_object_id(restaurant_id)
    if not rid:
        return 0
    restaurant = db.restaurants.find_one({"_id": rid, "is_active": True})
    if not restaurant:
        return 0
    if restaurant.get("is_recommended"):
        base_total = sum(int(item.get("total", 0)) for item in order_items)
    else:
        item_ids = [item.get("menu_item_id") for item in order_items if item.get("menu_item_id")]
        if not item_ids:
            return 0
        rec_items = list(db.menu_items.find({"_id": {"$in": item_ids}, "is_recommended": True}))
        rec_ids = {item.get("_id") for item in rec_items}
        if not rec_ids:
            return 0
        base_total = sum(
            int(item.get("total", 0))
            for item in order_items
            if item.get("menu_item_id") in rec_ids
        )
    if base_total <= 0:
        return 0
    adjusted_total = int(round(base_total * float(surge_multiplier or 1.0)))
    return int(adjusted_total // reward_services.REWARD_POINT_VALUE_PAISE)


def create_order(
    user_id: str,
    restaurant_id: str,
    items: List[Dict],
    payment_mode: str,
    wallet_amount: Optional[int],
    redeem_points: Optional[int] = None,
):
    db = get_db()
    rid = to_object_id(restaurant_id)
    if not rid:
        raise ValueError("Invalid restaurant id")
    restaurant = db.restaurants.find_one({"_id": rid, "is_active": True})
    if not restaurant:
        raise ValueError("Restaurant not found")

    order_items, subtotal = calculate_food_totals(restaurant_id, items)
    pickup_location = restaurant.get("location")
    surge_data = None
    surge_multiplier = 1.0
    if pickup_location and pickup_location.get("coordinates"):
        try:
            surge_data = pricing_services.calculate_surge(
                "ORDER",
                pickup_location["coordinates"][1],
                pickup_location["coordinates"][0],
            )
            surge_multiplier = float(surge_data.get("surge_multiplier", 1.0))
        except Exception:
            surge_multiplier = 1.0
    total_amount = pricing_services.apply_surge(subtotal, surge_multiplier)
    surge_amount = max(0, total_amount - subtotal)
    mode = normalize_payment_mode(payment_mode)
    if not mode:
        raise ValueError("Invalid payment mode")

    reward_points_earned = calculate_recommended_reward_points(restaurant_id, order_items, surge_multiplier)
    redeem_points_applied = 0
    redeem_amount = 0
    if redeem_points is not None:
        redeem_points_applied, redeem_amount, _ = reward_services.calculate_redeemable_points(
            user_id,
            total_amount,
            redeem_points,
        )
    total_after_rewards = max(0, total_amount - redeem_amount)

    wallet_to_use = 0
    if mode == "WALLET":
        wallet_to_use = int(wallet_amount or total_after_rewards)
        if wallet_to_use < total_after_rewards:
            raise ValueError("Wallet amount must cover the full total")
        if wallet_to_use > total_after_rewards:
            wallet_to_use = total_after_rewards
    elif mode == "WALLET_RAZORPAY":
        wallet_to_use = int(wallet_amount or 0)
        if wallet_to_use < 0 or wallet_to_use > total_after_rewards:
            raise ValueError("Invalid wallet amount")
    elif mode == "COD" and wallet_amount:
        raise ValueError("Wallet not allowed with COD")

    payment_amount = total_after_rewards - wallet_to_use
    order_id = ObjectId()
    wallet_txn = None
    reward_txn = None

    if wallet_to_use > 0:
        wallet_txn = wallet_services.debit_wallet(
            user_id,
            wallet_to_use,
            "FOOD_ORDER",
            "FOOD",
            reference=str(order_id),
        )
        if not wallet_txn:
            raise ValueError("Insufficient wallet balance")

    order_doc = {
        "_id": order_id,
        "user_id": to_object_id(user_id),
        "restaurant_id": rid,
        "status": "PLACED" if payment_amount == 0 or mode == "COD" else "PENDING_PAYMENT",
        "payment_mode": mode,
        "amount_subtotal": subtotal,
        "amount_total": total_after_rewards,
        "amount_total_before_rewards": total_amount,
        "surge_multiplier": round(surge_multiplier, 2),
        "surge_amount": surge_amount,
        "surge_meta": surge_data,
        "wallet_amount": wallet_to_use,
        "reward_redeem_amount": redeem_amount,
        "points_redeemed": redeem_points_applied,
        "reward_points_earned": reward_points_earned,
        "points_earned": 0,
        "payment_amount": payment_amount,
        "is_paid": payment_amount == 0,
        "job_status": "CREATED",
        "current_offer": None,
        "job_attempts": 0,
        "rejected_captains": [],
        "pickup_location": pickup_location,
        "created_at": utcnow(),
        "captain_id": None,
        "rewarded": False,
    }

    try:
        db.orders.insert_one(order_doc)
        db.order_items.insert_many([
            {
                "order_id": order_id,
                "menu_item_id": item["menu_item_id"],
                "name": item["name"],
                "price": item["price"],
                "quantity": item["quantity"],
                "total": item["total"],
                "created_at": utcnow(),
            }
            for item in order_items
        ])

        if redeem_points_applied > 0:
            reward_txn = reward_services.redeem_reward_points(
                user_id,
                redeem_points_applied,
                related_order=str(order_id),
            )
            if not reward_txn:
                raise ValueError("Insufficient reward points")

        razorpay_order = None
        if payment_amount > 0 and mode in {"RAZORPAY", "WALLET_RAZORPAY"}:
            razorpay_order = payment_services.create_razorpay_order(
                amount=payment_amount,
                receipt=f"order_{order_id}",
            )
            db.orders.update_one(
                {"_id": order_id},
                {"$set": {"razorpay_order_id": razorpay_order.get("id")}},
            )

        notification_services.send_to_user(
            user_id,
            "Order created",
            "Your order has been placed.",
            {"order_id": str(order_id)},
        )
        if pickup_location:
            try:
                matching_service.create_job("ORDER", str(order_id))
            except Exception:
                db.orders.update_one(
                    {"_id": order_id},
                    {"$set": {"job_status": "MATCHING_FAILED"}},
                )
        else:
            db.orders.update_one(
                {"_id": order_id},
                {"$set": {"job_status": "NO_LOCATION"}},
            )

        if payment_amount == 0 and mode != "COD":
            award_food_points(str(order_id))
        order_doc = db.orders.find_one({"_id": order_id})
        return order_doc, order_items, razorpay_order
    except Exception as exc:
        db.orders.update_one({"_id": order_id}, {"$set": {"status": "FAILED"}})
        if wallet_txn:
            wallet_services.refund_wallet(
                user_id,
                wallet_to_use,
                "ORDER_FAILED",
                "FOOD",
                reference=str(order_id),
            )
        if reward_txn:
            reward_services.credit_reward_points(
                user_id,
                redeem_points_applied,
                reward_services.REWARD_SOURCE_RECOMMENDATION,
                related_order=str(order_id),
            )
        raise exc


def verify_order_payment(order_id: str, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str):
    db = get_db()
    oid = to_object_id(order_id)
    if not oid:
        raise ValueError("Invalid order id")

    payment_services.verify_razorpay_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature)

    result = db.orders.update_one(
        {"_id": oid},
        {"$set": {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
            "is_paid": True,
            "status": "PLACED",
        }},
    )
    if result.matched_count == 0:
        raise ValueError("Order not found")
    award_food_points(order_id)
    return db.orders.find_one({"_id": oid})


def award_food_points(order_id: str):
    db = get_db()
    oid = to_object_id(order_id)
    if not oid:
        return None
    order_doc = db.orders.find_one({"_id": oid})
    if not order_doc or order_doc.get("rewarded"):
        return None
    if not order_doc.get("is_paid") and order_doc.get("payment_mode") != "COD":
        return None
    points = int(order_doc.get("reward_points_earned") or 0)
    if points <= 0:
        db.orders.update_one({"_id": oid}, {"$set": {"rewarded": True, "points_earned": 0}})
        return None
    txn = reward_services.credit_reward_points(
        str(order_doc.get("user_id")),
        points,
        reward_services.REWARD_SOURCE_ADMIN_RECOMMENDATION,
        related_order=str(order_id),
    )
    db.orders.update_one({"_id": oid}, {"$set": {"rewarded": True, "points_earned": points}})
    if txn:
        try:
            notification_services.send_to_user(
                str(order_doc.get("user_id")),
                "Rewards earned",
                f"You earned {points} reward points on your order.",
                {"order_id": str(order_id), "points": points},
            )
        except Exception:
            pass
    return txn
