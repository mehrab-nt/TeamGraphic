from rest_framework import filters
from rest_framework.response import Response
from api.permissions import ApiAccess
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from api.responses import TG_DATA_NOT_FOUND
from .models import AlarmMessage, Department, SmsMessage, WebMessage, MessageStatus, MessageType, WebMessageContent, \
    WebMessageType
from .serializers import AlarmMessageSerializer, DepartmentSerializer, SmsMessageSerializer, \
    WebMessageSerializer, WebMessageFileAccessSerializer, WebMessageGroupSendingSerializer, \
    WebMessageRequestNewSerializer, WebMessageSendNewSerializer, WebMessageWithContentSerializer, \
    WebMessageContentEmployeeResponseSerializer, WebMessageContentUserResponseSerializer
from user.models import User
from drf_spectacular.utils import extend_schema
from api.mixins import CustomMixinModelViewSet
from .filters import SmsMessageFilter, WebMessageFilter
from rest_framework.exceptions import PermissionDenied


@extend_schema(tags=['Message'])
class DepartmentViewSet(CustomMixinModelViewSet):
    """
    MEH: Department Model viewset
    """
    queryset = Department.objects.all().prefetch_related('employees')
    serializer_class = DepartmentSerializer
    pagination_class = None
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['department_manager']
    }
    cache_key = 'department_list'

    def list(self, request, *args, **kwargs): # MEH: for set time out to 1 year (always!)
        return super().list(request, timeout=60 * 60 * 24 * 365)


@extend_schema(tags=['Message'])
class SmsMessageViewSet(CustomMixinModelViewSet):
    """
    MEH: Sms Message model Viewset history (READ-Only)
    """
    queryset = SmsMessage.objects.select_related('receiver')
    serializer_class = SmsMessageSerializer
    http_method_names = ['get', 'head', 'options'] # MEH: Read only
    filterset_class = SmsMessageFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    search_fields = ['receiver__phone_number']
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['sms_history']
    }


@extend_schema(tags=['Message'])
class WebMessageViewSet(CustomMixinModelViewSet):
    """
    MEH: Web Message model Viewset
    """
    queryset = WebMessage.objects.all()
    serializer_class = WebMessageSerializer
    http_method_names = ['get', 'head', 'options', 'delete'] # MEH: Just read & create & destroy
    filterset_class = WebMessageFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    search_fields = ['user__first_name', 'user__phone_number']
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['message_manager'],
        'destroy': ['delete_message'],
        **dict.fromkeys(['list', 'retrieve'], ['message_manager', 'customer_message']),
        ** dict.fromkeys(['request_message', 'user_response'], ['customer_message'])
    }
    cache_key = 'web_message_list'

    def get_queryset(self):
        qs = super().get_queryset().select_related('user', 'department', 'employee')
        user = self.request.user
        if user.is_superuser:
            return qs
        if getattr(user, 'employee_profile', False):
            return qs.filter(department__in=user.employee_profile.department_list.all()) # MEH: See only related department
        return qs.filter(user=user) # MEH: Only own obj

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return WebMessageWithContentSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['put', 'patch'], http_method_names = ['put', 'patch'],
            url_path='file-access', serializer_class=WebMessageFileAccessSerializer, filter_backends=[None])
    def file_access(self, request, pk=None):
        """
        MEH: Active filee access in Web Message until User can upload file
        """
        web_message = self.get_object(pk=pk)
        return self.custom_update(web_message, request, partial=(request.method == 'PATCH'))

    @action(detail=False, methods=['post'], http_method_names = ['post'],
            url_path='send-new-message', serializer_class=WebMessageSendNewSerializer, filter_backends=[None])
    def send_new_message(self, request):
        """
        MEH: Send new message for user (select) from employee (auto set)
        auto create WebMessage topic
        """
        if hasattr(request.user, 'employee_profile'): # MEH: Just make sure, employee got here
            return self.custom_create(request, employee=request.user.employee_profile)
        raise PermissionDenied

    @action(detail=False, methods=['post'], http_method_names = ['post'],
            url_path='request-new-message', serializer_class=WebMessageRequestNewSerializer, filter_backends=[None])
    def request_new_message(self, request):
        """
        MEH: User first request send message to department (select)
        """
        return self.custom_create(request, user=request.user)

    @action(detail=False, methods=['get'], http_method_names = ['get'],
            url_path='my-list')
    def my_list(self, request):
        """
        MEH: Employee see all web message that interact with
        """
        web_messages = self.get_queryset().filter(employee=request.user.employee_profile)
        return self.custom_get(web_messages)

    @action(detail=True, methods=['post'], http_method_names=['post'],
            url_path='employee-response', serializer_class=WebMessageContentEmployeeResponseSerializer, filter_backends=[None])
    def employee_response(self, request, pk=None):
        """
        MEH: Employee response last message in Web Message Content
        """
        web_message = self.get_object(pk=pk)
        return self.custom_create(request, parent=web_message, type=MessageType.SEND)

    @action(detail=True, methods=['post'], http_method_names=['post'],
            url_path='user-response', serializer_class=WebMessageContentUserResponseSerializer, filter_backends=[None])
    def user_response(self, request, pk=None):
        """
        MEH: User response last message in Web Message Content
        """
        web_message = self.get_object(pk=pk)
        return self.custom_create(request, parent=web_message, type=MessageType.RECEIVE, status=MessageStatus.PENDING)

    @action(detail=False, methods=['post'], http_method_names = ['post'],
            url_path='send-group-message', serializer_class=WebMessageGroupSendingSerializer, filter_backends=[None])
    def send_group_message(self, request, pk=None):
        """
        MEH: Sending message to group of User (select) from employee (auto set)
        auto create WebMessage topic for all (manually)
        """
        data = self.get_validate_data(request.data)
        users = User.objects.filter(is_employee=False)
        if data.get('role'):
            users = users.filter(role=data['role'])
        if data.get('users'):
            ids = [u.id for u in data['users']]
            users = users.filter(id__in=ids)
        if not users.exists():
            return Response(TG_DATA_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        employee = getattr(request.user, 'employee_profile', None)
        web_messages = [ # MEH: STEP 1 -> Create WebMessage objects
            WebMessage(
                title=data.get('title'),
                user=user,
                employee=employee,
                department=data.get('department'),
                status=MessageStatus.ADMIN,
                type=WebMessageType.MESSAGE
            )
            for user in users
        ]
        batch_size = 1000 # MEH: STEP 2 -> Bulk create messages (now they have IDs)
        for i in range(0, len(web_messages), batch_size):
            WebMessage.objects.bulk_create(web_messages[i:i + batch_size])
        contents = [ # MEH: STEP 3 -> Now create related WebMessageContent objects
            WebMessageContent(
                parent=message,
                content=data['content'],
                type=MessageType.SEND
            )
            for message in web_messages
        ]
        for i in range(0, len(contents), batch_size):
            WebMessageContent.objects.bulk_create(contents[i:i + batch_size])
        return Response({"detail": f"{len(web_messages)} messages sent."}, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Message'])
class AlarmMessageViewSet(CustomMixinModelViewSet):
    """
    MEH: Alarm Message Model viewset
    """
    queryset = AlarmMessage.objects.all().select_related('employee').prefetch_related('roles').order_by('-create_date')
    serializer_class = AlarmMessageSerializer
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['alarm_message_manager'],
        'create': ['alarm_message_create']
    }
    cache_key = 'alarm_message_list'

    def list(self, request, *args, **kwargs): # MEH: for set time out to 1 year (always!)
        return super().list(request, timeout=60 * 60 * 24 * 365, *args, **kwargs)

    def create(self, request, *args, **kwargs): # MEH: for parse employee that create this alarm
        if hasattr(request.user, 'employee_profile'): # MEH: Just make sure, employee got here
            return super().create(request, employee=request.user.employee_profile)
        raise PermissionDenied

    def update(self, request, *args, **kwargs): # MEH: for parse employee that update this alarm
        if hasattr(request.user, 'employee_profile'): # MEH: Just make sure, employee got here
            return super().update(request, employee=request.user.employee_profile)
        raise PermissionDenied

    def partial_update(self, request, *args, **kwargs): # MEH: like update
        if hasattr(request.user, 'employee_profile'): # MEH: Just make sure, employee got here
            return super().partial_update(request, employee=request.user.employee_profile)
        raise PermissionDenied
