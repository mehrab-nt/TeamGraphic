from rest_framework.routers import DefaultRouter
from .views import ApiCategoryViewSet, ApiItemViewSet
import importlib
from django.apps import apps

router = DefaultRouter()
router.register(r'access-category', ApiCategoryViewSet, basename='api-access')
router.register(r'access-item', ApiItemViewSet, basename='api-access-item')

def get_combined_router():
    combined_router = DefaultRouter()
    for app_config in apps.get_app_configs():
        try:
            module = importlib.import_module(f"{app_config.name}.routers")
            router_item = getattr(module, "router", None)
            if router_item:
                for prefix, viewset, basename in getattr(router_item, "registry", []):
                    combined_router.register(prefix, viewset, basename=basename)
        except ModuleNotFoundError:
            continue  # MEH: No routers.py in this app, skip
    return combined_router
