from django.http import JsonResponse
from django.urls import resolve
from rest_framework.exceptions import AuthenticationFailed

from core.auth import get_user_from_request


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
