from rest_framework import permissions


class IsUserAdmin(permissions.BasePermission):
    """Check if User is Admin."""
    def has_permission(self, request, view):
        return not request.user.is_authenticated or request.user.is_admin


class IsUserAdminOrReadOnly(permissions.BasePermission):
    """Check if User is Admin or allow only GET method."""
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin)


class ReviewsCommentsPermission(permissions.BasePermission):
    """Permissions for Reviews and Comments."""
    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user
                or request.method in permissions.SAFE_METHODS
                or request.user.is_admin or request.user.is_moderator)


class TitlePermission(permissions.BasePermission):
    """Permissions for Titles."""
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin)


class AdminModeratorAuthorPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
