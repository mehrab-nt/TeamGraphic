from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import filters
from rest_framework.decorators import action
from api.mixins import CustomMixinModelViewSet
from api.serializers import BulkListSerializer, SendSignalSerializer
from .models import Company, Deposit, DepositConfirmStatus, BankAccount, CashBackPercent, CashBack, DepositType
from api.permissions import ApiAccess
from .serializers import DepositSerializer, DepositBriefListSerializer, DepositCreateSerializer, DepositOnlineListSerializer, \
    DepositPendingListSerializer, DepositPendingSetStatusSerializer, CompanySerializer, CompanyBriefSerializer, \
    BankAccountSerializer, BankAccountBriefSerializer, CashBackPercentSerializer, CashBackSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import DepositFilter
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from api.responses import TG_DATA_CREATED


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

    def get_serializer_class(self):
        if self.action == 'list':
            return CompanyBriefSerializer
        return super().get_serializer_class()


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
    required_api_keys = {
        '__all__': ['financial_document'],
        **dict.fromkeys(['pending_list', 'pending_deposit_set_status', 'retrieve',], ['pending_list']),
        'online_list': ['online_list', 'retrieve'],
        'create_deposit': ['create_deposit']
    }

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

    @action(detail=False, methods=['get'],
            url_path='online-list', serializer_class=DepositOnlineListSerializer, filter_backends=[None])
    def online_list(self, request):
        """
        MEH: Deposit Online List View for check
        """
        deposit_list = self.get_queryset().select_related('bank').filter(deposit_type=DepositType.WEBSITE)
        return self.custom_get(deposit_list)


@extend_schema(tags=['Financial'])
class OfflineBankAccountViewSet(CustomMixinModelViewSet):
    """
    MEH: Bank Account Model viewset (Offline)
    """
    queryset = BankAccount.objects.all().filter(is_online=False)
    serializer_class = BankAccountSerializer
    permission_classes = [ApiAccess]
    required_api_keys = {} # MEH: Empty mean just Admin can Access

    def get_serializer_class(self):
        if self.action == 'list':
            return BankAccountBriefSerializer
        return super().get_serializer_class()


@extend_schema(tags=['Financial'])
class OnlineBankAccountViewSet(OfflineBankAccountViewSet):
    """
    MEH: Bank Account Model viewset (Online)
    """
    def create(self, request, *args, **kwargs):
        return self.custom_create(request, is_online=True)


@extend_schema(tags=['Financial'])
class CashBackPercentViewSet(CustomMixinModelViewSet):
    """
    MEH: Cash Back Percent Model viewset
    """
    queryset = CashBackPercent.objects.all()
    serializer_class = CashBackPercentSerializer
    permission_classes = [ApiAccess]
    required_api_keys = {} # MEH: Empty mean just Admin can Access


@extend_schema(tags=['Financial'])
class CashBackViewSet(CustomMixinModelViewSet):
    """
    MEH: Cash Back Model viewset
    """
    queryset = CashBack.objects.all()
    serializer_class = CashBackSerializer
    http_method_names = ['get', 'put', 'patch', 'head', 'options']
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['credit__owner__first_name', 'credit__owner__last_name', 'credit__owner__phone_number']
    ordering_fields = ['now_total_order_amount', 'now_cashback']
    permission_classes = [ApiAccess]
    required_api_keys = {} # MEH: Empty mean just Admin can Access

    def get_queryset(self):
        qs = super().get_queryset().select_related('credit__owner').prefetch_related('valid_category')
        if self.action in ['confirm', 'bulk_confirm']:
            qs = qs.filter(last_confirm=False)
        return qs

    @extend_schema(
        summary='Confirm a list of Cashback',
        request=BulkListSerializer,
        responses={
           200: OpenApiResponse(description="Successfully confirmed List."),
           400: OpenApiResponse(description="Invalid IDs or constraint violation."),
        },
    )
    @action(detail=False, methods=['post'], http_method_names=['post'], serializer_class=BulkListSerializer,
            url_path='bulk-confirm')
    def bulk_confirm(self, request):
        """
        MEH: Confirm and increase credit for List of Cashback Objects (use POST ACTION for sending list of id `ids` in request body)
        """
        validated_data = self.get_validate_data(request.data)
        ids = validated_data['ids']
        cashback_list = self.get_queryset().filter(id__in=ids)
        if hasattr(request.user, 'employee_profile'): # MEH: Just make sure, employee got here
            employee = request.user.employee_profile
            result_list = []
            for cashback in cashback_list:
                value = cashback.confirm_cashback(employee)
                result_list.append({
                    "user": str(cashback.credit.owner),
                    "value": str(value)
                })
            return Response({"detail": TG_DATA_CREATED, "results": result_list}, status=status.HTTP_201_CREATED)
        raise PermissionDenied

    @extend_schema(summary='Confirm Cashback')
    @action(detail=True, methods=['post'], http_method_names=['post'], serializer_class=SendSignalSerializer,
            url_path='confirm')
    def confirm(self, request, pk=None):
        """
        MEH: Confirm and increase credit for Cashback Objects
        """
        cashback = self.get_object(pk=pk)
        if hasattr(request.user, 'employee_profile'): # MEH: Just make sure, employee got here
            employee = request.user.employee_profile
            value = cashback.confirm_cashback(employee)
            return Response({"detail": TG_DATA_CREATED,"results": {"user": str(cashback.credit.owner), "value": str(value)}}, status=status.HTTP_201_CREATED)
        raise PermissionDenied
