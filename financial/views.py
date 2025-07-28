from drf_spectacular.utils import extend_schema
from rest_framework import filters
from rest_framework.decorators import action
from api.mixins import CustomMixinModelViewSet
from .models import Company, Deposit, DepositConfirmStatus
from api.permissions import ApiAccess
from .serializers import DepositSerializer, DepositBriefListSerializer, DepositCreateSerializer, \
    DepositPendingListSerializer, DepositPendingSetStatusSerializer, CompanySerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import DepositFilter
from rest_framework.exceptions import PermissionDenied


@extend_schema(tags=['Financial'])
class CompanyViewSet(CustomMixinModelViewSet):
    """
    MEH: Company Model viewset
    """
    queryset = Company.objects.all().select_related('agent', 'city', 'province')
    serializer_class = CompanySerializer
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = ['name', 'agent__first_name']
    permission_classes = [ApiAccess]
    required_api_keys = {} # MEH: Empty mean just Admin can Access


@extend_schema(tags=['Financial'])
class DepositViewSet(CustomMixinModelViewSet):
    """
    MEH: Deposit Model viewset
    """
    queryset = Deposit.objects.all().order_by('-submit_date')
    serializer_class = DepositSerializer
    http_method_names = ['get', 'delete', 'head', 'options']
    filterset_class = DepositFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    search_fields = ['description']
    permission_classes = [ApiAccess]
    required_api_keys = {} # MEH: Empty mean just Admin can Access

    def get_queryset(self):
        qs = super().get_queryset()
        if action == 'pending_list':
            return qs.select_related('credit__owner', 'submit_by', 'confirm_by', 'bank').filter(confirm_status=DepositConfirmStatus.PENDING)
        if action == 'pending_deposit_set_status':
            return qs.filter(confirm_status=DepositConfirmStatus.PENDING)
        return qs.select_related('credit__owner', 'submit_by', 'confirm_by')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DepositBriefListSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['post'], http_method_names=['post'],
            url_path='create', serializer_class=DepositCreateSerializer, filter_backends=[None])
    def create_deposit(self, request):
        """
        MEH: Create manual Deposit from Employee
        """
        if hasattr(request.user, 'employee_profile'): # MEH: Just make sure, employee got here
            return self.custom_create(request, submit_by=request.user.employee_profile)
        raise PermissionDenied

    @action(detail=False, methods=['get'],
            url_path='pending-list', serializer_class=DepositPendingListSerializer, filter_backends=[None])
    def pending_list(self, request):
        """
        MEH: Deposit Pending List View for check and confirm
        """
        deposit_list = self.get_queryset().select_related('bank').filter(confirm_status=DepositConfirmStatus.PENDING)
        return self.custom_get(deposit_list)

    @action(detail=True, methods=['put', 'patch'], http_method_names=['put', 'patch'],
            url_path='set-status', serializer_class=DepositPendingSetStatusSerializer, filter_backends=[None])
    def pending_deposit_set_status(self, request, pk=None):
        """
        MEH: Deposit Pending List set confirm status
        """
        deposit = self.get_object(pk=pk)
        return self.custom_update(deposit, request, partial=(request.method == 'PATCH'))
