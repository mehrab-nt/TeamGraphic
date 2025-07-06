from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .responses import TG_PERMISSION_DENIED


class ApiAccess(permissions.BasePermission):
    # MEH: Check permission before get_queryset and get_object
    def has_permission(self, request, view): # Check if User is logged for get access to queryset
        if view.action is None:
            return True
        get_key_fn = getattr(view, 'get_required_api_key', None)
        if callable(get_key_fn):
            required_key = get_key_fn()
        else:
            required_key = None
        if required_key:
            if not request.user.is_authenticated:
                raise PermissionDenied(TG_PERMISSION_DENIED)
            print(f"[PERMISSION] Checking key: {required_key} for user: {request.user}")
            if not request.user.has_api_permission(required_key):
                raise PermissionDenied(TG_PERMISSION_DENIED)
        return True

    # MEH: Check permission after get_object to handle if user is allowed or not
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
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
