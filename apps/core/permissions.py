from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Object-level permission: user may only touch rows they own."""

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "user_id", None) == request.user.id
