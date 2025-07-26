from rest_framework.routers import DefaultRouter
from .views import FileDirectoryViewSet, FileItemViewSet

router = DefaultRouter()
router.register(r'file-manager/directory', FileDirectoryViewSet, basename='file-directory')
router.register(r'file-manager/item', FileItemViewSet, basename='file-item')
