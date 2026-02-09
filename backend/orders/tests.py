from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from bson import ObjectId
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from orders import services as order_services
from orders.views import OrderCheckoutView


class OrderRewardTests(TestCase):
    def test_award_food_points_for_recommendations(self):
        order_id = ObjectId()
        user_id = ObjectId()
        restaurant_id = ObjectId()
        fake_db = MagicMock()
        fake_db.orders.find_one.return_value = {
            "_id": order_id,
            "user_id": user_id,
            "restaurant_id": restaurant_id,
            "is_paid": True,
            "payment_mode": "RAZORPAY",
            "rewarded": False,
        }
        fake_db.order_items.find.return_value = [
            {"menu_item_id": ObjectId(), "total": 5000}
        ]

        with patch("orders.services.get_db", return_value=fake_db), \
             patch("orders.services.recommendation_services.calculate_recommendation_points", return_value=25), \
             patch("orders.services.reward_services.credit_reward_points", return_value={"_id": ObjectId()}):
            txn = order_services.award_food_points(str(order_id))

        self.assertIsNotNone(txn)
        fake_db.orders.update_one.assert_any_call(
            {"_id": order_id},
            {"$set": {"rewarded": True, "points_earned": 25}},
        )


class OrderCheckoutRewardTests(TestCase):
    def test_checkout_applies_reward_points(self):
        factory = APIRequestFactory()
        request = factory.post(
            "/api/v1/orders/checkout/",
            {
                "restaurant_id": "restaurant",
                "items": [{"menu_item_id": "menu", "quantity": 1}],
                "redeem_points": 10,
            },
            format="json",
        )
        user = SimpleNamespace(id="user", role="USER", is_authenticated=True)
        force_authenticate(request, user=user)

        with patch("orders.views.services.calculate_food_totals", return_value=([{"menu_item_id": "menu", "quantity": 1, "total": 5000}], 5000)), \
             patch("orders.views.get_db") as mock_db, \
             patch("orders.views.reward_services.calculate_redeemable_points", return_value=(10, 1000, 50)):
            mock_db.return_value.restaurants.find_one.return_value = {"location": None}
            response = OrderCheckoutView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["redeem_points_applied"], 10)
        self.assertEqual(response.data["total"], 4000)
