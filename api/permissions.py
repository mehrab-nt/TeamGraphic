from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .responses import TG_PERMISSION_DENIED


class ApiAccess(permissions.BasePermission):
    """
    MEH: Handle Access For Employee (Api-Item in Employee-Level)
    """
    def has_permission(self, request, view): # MEH: Check permission before get_queryset and get_object
        if view.action is None:
            return True
        get_key_fn = getattr(view, 'get_required_api_key', None)
        if callable(get_key_fn):
            required_key = get_key_fn()
        else:
            required_key = None
        if required_key:
            if required_key == 'allow_any': # MEH: Set action key (allow_any) -> Show to any User even not authenticated
                return True
            elif request.user.is_authenticated: # MEH: If There is a key except (allow_any), so User most be authenticated
                # todo: remove this print for publish
                print(f"[PERMISSION] Checking key: {required_key} for user: {request.user}") # MEH: Log what User try to Access what Api...
                if request.user.has_api_permission(required_key): # MEH: Check Api-Item list in Employee-Level (Super User Access it anyway)
                    return True
        elif request.user.is_authenticated:
            if request.user.is_superuser: # MEH: If User Is SuperUser, Show it anyway (also in ths way)
                return True
        raise PermissionDenied(TG_PERMISSION_DENIED)

    def has_object_permission(self, request, view, obj): # MEH: Check permission after get_object to handle if user is allowed or not for sure
        if request.user.is_authenticated:
            target_user = getattr(obj, 'user', obj) # MEH: Check if user want to access their Data or is Admin pr Employee
            if target_user == request.user or request.user.is_superuser or request.user.is_employee:
                return True
        raise PermissionDenied(TG_PERMISSION_DENIED)


class IsNotAuthenticated(permissions.BasePermission):
    """
    MEH: Handle Access for module that need User not authenticated
    Like -> User most be not Authenticated for SignUp, SignIn, ...
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated and not request.user.is_superuser:
            raise PermissionDenied(TG_PERMISSION_DENIED)
        return True
