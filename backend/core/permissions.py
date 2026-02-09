from rest_framework.permissions import BasePermission


class RolePermission(BasePermission):
    def has_permission(self, request, view):
        allowed_roles = getattr(view, "allowed_roles", None)
        if not allowed_roles:
            return True
        role = getattr(request.user, "role", None) or getattr(request, "role", None)
        return role in allowed_roles
