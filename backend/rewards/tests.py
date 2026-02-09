from unittest.mock import patch
from django.test import TestCase

from rewards import services as reward_services


class RewardServiceTests(TestCase):
    def test_calculate_redeemable_points(self):
        with patch("rewards.services.get_reward_balance", return_value=100):
            points, amount, available = reward_services.calculate_redeemable_points(
                "user",
                total_amount_paise=20000,
                requested_points=50,
            )
        self.assertEqual(points, 50)
        self.assertEqual(amount, 5000)
        self.assertEqual(available, 100)

    def test_calculate_redeemable_points_insufficient(self):
        with patch("rewards.services.get_reward_balance", return_value=10):
            with self.assertRaises(ValueError):
                reward_services.calculate_redeemable_points(
                    "user",
                    total_amount_paise=20000,
                    requested_points=50,
                )
