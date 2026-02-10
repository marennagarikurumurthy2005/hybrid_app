import base64
import hashlib
import json
import time
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.urls import resolve
from rest_framework.exceptions import AuthenticationFailed

from core.auth import get_user_from_request
from core.redis_queue import get_client

try:
    from prometheus_client import Counter, Histogram
    REQUEST_COUNT = Counter(
        "http_requests_total",
        "Total HTTP requests",
        ["method", "path", "status"],
    )
    REQUEST_LATENCY = Histogram(
        "http_request_duration_seconds",
        "HTTP request duration in seconds",
        ["method", "path"],
    )
except Exception:
    REQUEST_COUNT = None
    REQUEST_LATENCY = None


class RoleRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            match = resolve(request.path_info)
        except Exception:
            return self.get_response(request)

        view_func = match.func
        view_cls = getattr(view_func, "view_class", None)
        allowed_roles = getattr(view_cls, "allowed_roles", None)

        if allowed_roles:
            try:
                user_doc = get_user_from_request(request)
            except AuthenticationFailed as exc:
                return JsonResponse({"detail": str(exc)}, status=401)
            role = user_doc.get("role")
            if role not in allowed_roles:
                return JsonResponse({"detail": "Role not allowed"}, status=403)
            request.role = role
            request.user_doc = user_doc

        return self.get_response(request)


def _get_ip_address(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or "unknown"


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not getattr(settings, "RATE_LIMIT_ENABLED", False):
            return self.get_response(request)
        path = request.path_info or ""
        exempt = set(getattr(settings, "RATE_LIMIT_EXEMPT_PATHS", []) or [])
        if path in exempt:
            return self.get_response(request)

        limit = int(getattr(settings, "RATE_LIMIT_MAX_REQUESTS", 300))
        window = int(getattr(settings, "RATE_LIMIT_WINDOW_SEC", 60))
        ip = _get_ip_address(request)
        key = f"rl:{ip}:{request.method}:{path}"
        try:
            client = get_client()
            count = client.incr(key)
            if count == 1:
                client.expire(key, window)
            if count > limit:
                return JsonResponse(
                    {"detail": "Rate limit exceeded", "retry_after_sec": window},
                    status=429,
                )
        except Exception:
            pass
        return self.get_response(request)


class IdempotencyKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method != "POST":
            return self.get_response(request)
        idem_key = request.META.get("HTTP_IDEMPOTENCY_KEY")
        if not idem_key:
            return self.get_response(request)

        path = request.path_info or ""
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        token = auth.split(" ", 1)[1] if auth.startswith("Bearer ") else auth
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()[:12] if token else "anon"
        body_hash = hashlib.sha256(request.body or b"").hexdigest()
        cache_key = f"idemp:{request.method}:{path}:{token_hash}:{idem_key}"

        try:
            client = get_client()
            cached = client.get(cache_key)
            if cached:
                payload = json.loads(cached)
                if payload.get("request_hash") != body_hash:
                    return JsonResponse(
                        {"detail": "Idempotency key reuse with different payload"},
                        status=409,
                    )
                body = base64.b64decode(payload.get("body_b64") or "")
                resp = HttpResponse(body, status=payload.get("status", 200))
                if payload.get("content_type"):
                    resp["Content-Type"] = payload.get("content_type")
                resp["Idempotency-Replay"] = "true"
                return resp
        except Exception:
            cached = None

        response = self.get_response(request)
        try:
            if response.status_code in (200, 201, 202) and hasattr(response, "content"):
                ttl = int(getattr(settings, "IDEMPOTENCY_TTL_SEC", 86400))
                payload = {
                    "status": response.status_code,
                    "content_type": response.get("Content-Type", "application/json"),
                    "request_hash": body_hash,
                    "body_b64": base64.b64encode(response.content or b"").decode("utf-8"),
                }
                client = get_client()
                client.setex(cache_key, ttl, json.dumps(payload))
        except Exception:
            pass
        return response


class PrometheusMetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not REQUEST_COUNT or not REQUEST_LATENCY:
            return self.get_response(request)
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start
        path = request.path_info or ""
        REQUEST_COUNT.labels(request.method, path, str(response.status_code)).inc()
        REQUEST_LATENCY.labels(request.method, path).observe(duration)
        return response
