from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class IsPublicOrOwner(permissions.BasePermission):
    """
    Allow access to public objects or if user is the owner.
    """
    def has_object_permission(self, request, view, obj):
        if obj.is_public:
            return True
        return obj.owner == request.user


class IsOwner(permissions.BasePermission):
    """
    Permission to only allow owners of an object to access it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsNotificationOwner(permissions.BasePermission):
    """
    Permission to only allow users to access their own notifications.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsSavedPromptOwner(permissions.BasePermission):
    """
    Permission to only allow users to access their own saved prompts.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsCommentOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow anyone to read comments, but only owners can edit/delete.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
