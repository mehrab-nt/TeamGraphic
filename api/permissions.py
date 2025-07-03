from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .responses import TG_PERMISSION_DENIED


class CustomBasePermission(permissions.BasePermission):
    # MEH: Check permission before get_queryset and get_object
    def has_permission(self, request, view): # Check if Method safe & User is logged for get access to queryset
        if not request.user.is_authenticated:
            raise PermissionDenied(TG_PERMISSION_DENIED)
        return True

    # MEH: Check permission after get_object to handle if user is allowed or not
    def has_object_permission(self, request, view, obj):
        target_user = getattr(obj, 'user', obj) # MEH: Check if user want to access their Data or is Admin pr Employee
        if target_user != request.user and not request.user.is_superuser and not request.user.is_employee:
            raise PermissionDenied(TG_PERMISSION_DENIED)
        return True


# MEH: User most be not Authenticated for SignUp, SignIn, ...
class IsNotAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and not request.user.is_superuser:
            raise PermissionDenied(TG_PERMISSION_DENIED)
        return True


# MEH: Handle Api Access (User) for admin, employee and regular user ...
class UserApiAccess(CustomBasePermission):
    def has_permission(self, request, view):
        super().has_permission(request, view)
        if view.action is None:
            return True
        get_key_fn = getattr(view, 'get_required_api_key', None)
        if callable(get_key_fn):
            required_key = get_key_fn()
        else:
            required_key = None
        print(f"[PERMISSION] Checking key: {required_key} for user: {request.user}")
        if required_key:
            if not request.user.has_api_permission(required_key):
                raise PermissionDenied(TG_PERMISSION_DENIED)
        return True

    def has_object_permission(self, request, view, obj):
        super().has_permission(request, view)
        return True
