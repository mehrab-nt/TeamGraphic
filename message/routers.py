from rest_framework.routers import DefaultRouter
from .views import AlarmMessageViewSet, DepartmentViewSet, SmsMessageViewSet, WebMessageViewSet

router = DefaultRouter()
router.register(r'alarm', AlarmMessageViewSet, basename='alarm_message')
router.register(r'sms-history', SmsMessageViewSet, basename='sms_history')
router.register(r'web-message', WebMessageViewSet, basename='web-message')
router.register(r'department', DepartmentViewSet, basename='department')
