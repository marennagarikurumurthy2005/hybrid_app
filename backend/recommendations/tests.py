from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from bson import ObjectId
from django.test import TestCase

from recommendations import services as recommendation_services


class RecommendationServiceTests(TestCase):
    def test_create_recommendation_invalid_reference(self):
        fake_db = MagicMock()
        fake_db.restaurants.find_one.return_value = None
        with patch("recommendations.services.get_db", return_value=fake_db):
            with self.assertRaises(ValueError):
                recommendation_services.create_recommendation(
                    created_by=str(ObjectId()),
                    rec_type="RESTAURANT",
                    reference_id="invalid",
                    title="Top Pick",
                    description="Admin choice",
                )

    def test_create_and_delete_recommendation(self):
        restaurant_id = ObjectId()
        created_by = ObjectId()
        recommendation_id = ObjectId()
        fake_db = MagicMock()
        fake_db.restaurants.find_one.return_value = {"_id": restaurant_id, "is_active": True}
        fake_db.recommendations.insert_one.return_value = SimpleNamespace(inserted_id=recommendation_id)
        fake_db.recommendations.delete_one.return_value = SimpleNamespace(deleted_count=1)

        with patch("recommendations.services.get_db", return_value=fake_db):
            rec = recommendation_services.create_recommendation(
                created_by=str(created_by),
                rec_type="RESTAURANT",
                reference_id=str(restaurant_id),
                title="Top Pick",
                description="Admin choice",
            )
            self.assertEqual(rec["_id"], recommendation_id)
            self.assertEqual(rec["type"], "RESTAURANT")

            deleted = recommendation_services.delete_recommendation(str(recommendation_id))
            self.assertTrue(deleted)
