from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .responses import TG_PERMISSION_DENIED


class ApiAccess(permissions.BasePermission):
    """
    MEH: Handle Access For Employee (Api-Item in Employee-Level) & normal User (Api-Item in Role)
    """
    def has_permission(self, request, view): # MEH: Check permission before get_queryset and get_object
        if view.action is None:
            return True
        required_keys = getattr(view, 'required_api_keys', {}).get(view.action) or \
                        getattr(view, 'required_api_keys', {}).get('__all__', [])
        if not isinstance(required_keys, list):
            required_keys = [required_keys]
        if 'allow_any' in required_keys: # MEH: Set action key (allow_any) -> Show to any User even not authenticated
            return True
        if request.user.is_authenticated: # MEH: If There is a key except (allow_any), so User most be authenticated
            if request.user.is_superuser or request.user.is_staff: # MEH: If User Is SuperUser, Show it anyway
                return True
            # print(f"[PERMISSION] Checking key: {required_keys} for: {request.user}") # MEH: Log what User try to Access what Api...
            if request.user.has_api_permission(required_keys): # MEH: Check Api-Item list in Employee-Level (Super User Access it anyway)
                return True
        raise PermissionDenied(TG_PERMISSION_DENIED)

    def has_object_permission(self, request, view, obj): # MEH: Check permission after get_object to handle if user is allowed or not for sure
        if request.user.is_authenticated:
            target_user = getattr(obj, 'user', obj) # MEH: Get User itself from obj or obj.user
            if target_user == request.user or request.user.is_superuser or request.user.is_employee: # MEH: Check if user want to access their Data or is Admin pr Employee
                return True
        raise PermissionDenied(TG_PERMISSION_DENIED)


class IsNotAuthenticated(permissions.BasePermission):
    """
    MEH: Handle Access for module that need User not authenticated (Even super_user)
    Like -> User most be not Authenticated for SignUp, SignIn, ...
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            raise PermissionDenied(TG_PERMISSION_DENIED)
        return True


class IsOwner(permissions.BasePermission):
    """
    MEH: Only Owner of object can access this
    Like -> Change Password
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            raise PermissionDenied(TG_PERMISSION_DENIED)
        target_user = getattr(obj, 'user', obj) # MEH: Get User itself from obj or obj.user
        if target_user == request.user:
            return True
        raise PermissionDenied(TG_PERMISSION_DENIED)
