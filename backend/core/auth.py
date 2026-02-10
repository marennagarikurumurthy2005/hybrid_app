from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import uuid
import jwt
from bson import ObjectId
from django.conf import settings
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from core.db import get_db


class MongoUser(SimpleNamespace):
    @property
    def is_authenticated(self):
        return True


def _generate_jti() -> str:
    return uuid.uuid4().hex


def create_access_token(user_doc: dict, jti: str = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_doc["_id"]),
        "phone": user_doc.get("phone"),
        "role": user_doc.get("role"),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.JWT_EXP_MINUTES)).timestamp()),
        "iss": settings.JWT_ISSUER,
        "typ": "access",
        "jti": jti or _generate_jti(),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_doc: dict, session_id: str = None, jti: str = None) -> str:
    now = datetime.now(timezone.utc)
    exp_minutes = int(getattr(settings, "JWT_REFRESH_EXP_MINUTES", 43200))
    payload = {
        "sub": str(user_doc["_id"]),
        "phone": user_doc.get("phone"),
        "role": user_doc.get("role"),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=exp_minutes)).timestamp()),
        "iss": settings.JWT_ISSUER,
        "typ": "refresh",
        "jti": jti or _generate_jti(),
    }
    if session_id:
        payload["sid"] = session_id
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, verify_type: str = None) -> dict:
    options = {"require": ["exp", "iat", "sub"]}
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        issuer=settings.JWT_ISSUER,
        options=options,
    )
    if verify_type and payload.get("typ") != verify_type:
        raise AuthenticationFailed("Invalid token type")
    return payload


def _is_token_blacklisted(jti: str) -> bool:
    if not jti:
        return False
    db = get_db()
    return db.token_blacklist.find_one({"jti": jti}) is not None


def is_token_blacklisted(jti: str) -> bool:
    return _is_token_blacklisted(jti)


def blacklist_token(jti: str, token_type: str, user_id: str, exp: int):
    if not jti:
        return False
    db = get_db()
    db.token_blacklist.update_one(
        {"jti": jti},
        {"$set": {
            "jti": jti,
            "token_type": token_type,
            "user_id": ObjectId(str(user_id)) if user_id else None,
            "exp": exp,
            "created_at": datetime.now(timezone.utc),
        }},
        upsert=True,
    )
    return True


def get_user_doc_by_token(token: str) -> dict:
    try:
        payload = decode_token(token, verify_type="access")
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationFailed("Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationFailed("Invalid token") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationFailed("Invalid token payload")

    db = get_db()
    try:
        oid = ObjectId(user_id)
    except Exception as exc:
        raise AuthenticationFailed("Invalid token payload") from exc

    jti = payload.get("jti")
    if jti and _is_token_blacklisted(jti):
        raise AuthenticationFailed("Token revoked")

    user_doc = db.users.find_one({"_id": oid, "is_active": True})
    if not user_doc:
        raise AuthenticationFailed("User not found or inactive")

    return user_doc


def get_user_from_request(request):
    auth = get_authorization_header(request).decode("utf-8")
    if not auth or not auth.startswith("Bearer "):
        raise AuthenticationFailed("Authentication credentials were not provided")
    token = auth.split(" ", 1)[1]
    return get_user_doc_by_token(token)


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).decode("utf-8")
        if not auth:
            return None
        if not auth.startswith("Bearer "):
            return None

        token = auth.split(" ", 1)[1]
        user_doc = get_user_doc_by_token(token)
        user = MongoUser(
            id=str(user_doc["_id"]),
            phone=user_doc.get("phone"),
            role=user_doc.get("role"),
        )
        request.user_doc = user_doc
        request.role = user_doc.get("role")
        return (user, None)
