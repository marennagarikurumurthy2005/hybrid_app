from core.geo_utils import ensure_captain_geo_index
from pricing import services as pricing_services
from ratings import services as ratings_services
from fraud import services as fraud_services
from maps import services as maps_services
from core.db import get_db


def main():
    ensure_captain_geo_index()
    pricing_services.ensure_indexes()
    ratings_services.ensure_indexes()
    fraud_services.ensure_indexes()
    maps_services.ensure_indexes()
    db = get_db()
    db.matching_logs.create_index("created_at", name="matching_logs_created_at")
    print("Indexes ensured.")


if __name__ == "__main__":
    main()
