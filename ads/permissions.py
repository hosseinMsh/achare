from __future__ import annotations

from rest_framework import permissions


def _has_role(user, *roles: str) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.roles.filter(name__in=[r.lower() for r in roles]).exists()


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return _has_role(request.user, 'customer')


class IsContractor(permissions.BasePermission):
    def has_permission(self, request, view):
        return _has_role(request.user, 'contractor')


class IsSupportOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return _has_role(request.user, 'support', 'admin')


class CanViewAdvertisement(permissions.BasePermission):
    """Object-level visibility rules for ads."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser or _has_role(user, 'support', 'admin'):
            return True

        # Owner can see all own ads.
        if obj.customer_id == user.id:
            return True

        # Assigned contractor can see.
        if obj.contractor_id == user.id:
            return True

        # Other contractors can see only OPEN ads (not canceled, not assigned).
        if _has_role(user, 'contractor') and obj.status == obj.STATUS_OPEN:
            return True

        return False
