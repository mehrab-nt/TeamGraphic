from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .responses import TG_PERMISSION_DENIED

# MEH: User most be not Authenticated for SignUp, SignIn, ...
class IsNotAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and not request.user.is_superuser:
            raise PermissionDenied(TG_PERMISSION_DENIED)
        return True

# MEH: Handle Api Access (User) for admin, employee and regular user ...
class UserApiAccess(permissions.BasePermission):
    # MEH: Check permission before get_queryset and get_object
    def has_permission(self, request, view):
        # if view.action == 'profile':
        #     return False
        # todo: check Employee api access from api model class
        if not request.user.is_authenticated:
            raise PermissionDenied(TG_PERMISSION_DENIED)
        return True

    # MEH: Check permission after get_object to handle if user is allowed or not
    def has_object_permission(self, request, view, obj):
        target_user = getattr(obj, 'user', obj)
        # todo: check Employee api access from api model class
        if not target_user != request.user and not request.user.is_superuser:
            raise PermissionDenied(TG_PERMISSION_DENIED)
        return True
