from datetime import datetime
from typing import List
import redis
from django.conf import settings

_client = None


def get_client():
    global _client
    if _client is None:
        _client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _client


def enqueue_job(job_id: str):
    client = get_client()
    client.rpush("jobs:queue", job_id)


def set_candidates(job_id: str, captain_ids: List[str]):
    client = get_client()
    key = f"job:{job_id}:candidates"
    client.delete(key)
    if captain_ids:
        client.rpush(key, *captain_ids)


def pop_candidate(job_id: str):
    client = get_client()
    key = f"job:{job_id}:candidates"
    return client.lpop(key)


def set_offer(job_id: str, captain_id: str, expires_at: datetime):
    client = get_client()
    key = f"job:{job_id}:offer"
    client.hset(key, mapping={
        "captain_id": captain_id,
        "expires_at": expires_at.isoformat(),
    })


def get_offer(job_id: str):
    client = get_client()
    key = f"job:{job_id}:offer"
    return client.hgetall(key)


def clear_offer(job_id: str):
    client = get_client()
    client.delete(f"job:{job_id}:offer")


def _ws_key(kind: str):
    if kind.endswith("s"):
        return f"ws:{kind}"
    return f"ws:{kind}s"


def set_ws_presence(kind: str, user_id: str, is_online: bool):
    client = get_client()
    key = _ws_key(kind)
    if is_online:
        client.sadd(key, user_id)
    else:
        client.srem(key, user_id)


def is_ws_online(kind: str, user_id: str) -> bool:
    client = get_client()
    key = _ws_key(kind)
    return client.sismember(key, user_id)
