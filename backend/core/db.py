from typing import Optional
from urllib.parse import urlparse
from django.conf import settings
from pymongo import MongoClient

_client = None
_db = None


def _parse_db_name(uri: Optional[str]):
    if not uri:
        return None
    parsed = urlparse(uri)
    if parsed.path and len(parsed.path) > 1:
        return parsed.path.lstrip("/").split("/")[0]
    return None


def get_db():
    global _client, _db
    if _db is None:
        if not settings.MONGO_URI:
            raise RuntimeError("MONGO_URI is not configured")
        _client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
        db_name = settings.MONGO_DB_NAME or _parse_db_name(settings.MONGO_URI)
        if not db_name:
            raise RuntimeError("MONGO_DB_NAME is not configured")
        _db = _client[db_name]
    return _db
