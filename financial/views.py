from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import filters
from rest_framework.decorators import action
from api.mixins import CustomMixinModelViewSet
from api.serializers import BulkListSerializer, SendSignalSerializer
from .models import Company, Deposit, DepositConfirmStatus, BankAccount, CashBackPercent, CashBack, DepositType, TransactionType
from api.permissions import ApiAccess
from .serializers import DepositSerializer, DepositBriefListSerializer, DepositCreateSerializer, \
    DepositOnlineListSerializer, \
    DepositPendingListSerializer, DepositPendingSetStatusSerializer, CompanySerializer, CompanyBriefSerializer, \
    BankAccountSerializer, BankAccountBriefSerializer, CashBackPercentSerializer, CashBackSerializer, \
    DepositDownloadDataSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import DepositFilter
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from api.responses import TG_DATA_CREATED
import jdatetime
from file_manager.excel_handler import ExcelHandler


@extend_schema(tags=['Financial'])
class CompanyViewSet(CustomMixinModelViewSet):
    """
    MEH: Company Model viewset
    """
    queryset = Company.objects.all().select_related('agent', 'city', 'province')
    serializer_class = CompanySerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['name', 'agent__first_name']
    ordering_fields = ['name', 'province']
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['company_manager'],
    }

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
    http_method_names = ['get', 'head', 'options']
    filterset_class = DepositFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    search_fields = ['description']
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['deposit_list'],
        **dict.fromkeys(['pending_list', 'pending_deposit_set_status', 'retrieve',], ['pending_list']),
        'online_list': ['deposit_list', 'online_list', 'retrieve'],
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
            url_path='pending-list', serializer_class=DepositPendingListSerializer)
    def pending_list(self, request):
        """
        MEH: Deposit Pending List View for check and confirm
        """
        deposit_list = self.filter_queryset(self.get_queryset().select_related('bank').filter(confirm_status=DepositConfirmStatus.PENDING))
        return self.custom_get(deposit_list)

    @action(detail=True, methods=['put', 'patch'], http_method_names=['put', 'patch'],
            url_path='set-status', serializer_class=DepositPendingSetStatusSerializer, filter_backends=[None])
    def pending_deposit_set_status(self, request, pk=None):
        """
        MEH: Deposit Pending List set confirm status
        """
        deposit = self.get_object(pk=pk)
        if hasattr(request.user, 'employee_profile'): # MEH: Just make sure, employee got here
            return self.custom_update(deposit, request, confirm_by=request.user.employee_profile, partial=(request.method == 'PATCH'))
        raise PermissionDenied

    @action(detail=False, methods=['get'],
            url_path='online-list', serializer_class=DepositOnlineListSerializer)
    def online_list(self, request):
        """
        MEH: Deposit Online List View for check
        """
        deposit_list = self.filter_queryset(self.get_queryset().select_related('bank').filter(transaction_type=TransactionType.ONLINE))
        return self.custom_get(deposit_list)

    @extend_schema(
        summary="Download Excel of Deposit list",
        responses={200: OpenApiTypes.BINARY},  # or a more specific file/media type
        parameters=[
            OpenApiParameter(
                name='check_field',
                description='Used for highlight Deposit row in Excel file, if check_filed is None or 0 in Excel cell',
                required=False,
                type=str,
                location='query',
                enum=list(DepositDownloadDataSerializer().get_fields().keys())
            )
        ]
    )
    @action(detail=False, methods=['get'],
            url_path='download', serializer_class=None)
    def download_deposit_list(self, request):
        """
        MEH: Direct Download Excel of Deposit List with Filter (up to 1000) (GET ACTION)
        """
        check_field = request.query_params.get('check_field')
        queryset = self.filter_queryset(self.get_queryset())[:10000]  # MEH: For apply filters/search/order like list()

        persian_header = {
            'user_display': 'نام مشتری',
            'submit_date': 'تاریخ ثبت',
            'deposit_date': 'تاریخ پرداخت',
            'deposit_type_display': 'نوع تراکنش',
            'receive_amount': 'بستانکار (تومان)',
            'pay_amount': 'بدهکار (تومان)',
            'description': 'توضیحات',
            'transaction_type_display': 'نحوه پرداحت',
        }
        serializer_class = DepositDownloadDataSerializer
        base_fields = list(serializer_class().get_fields().keys())
        headers = [persian_header.get(f, f) for f in base_fields]  # MEH: Get Header from Serializer

        rows = []
        for deposit in queryset:
            serializer = serializer_class(deposit)
            row = []
            for field in base_fields:
                value = serializer.data.get(field)

                # Convert Gregorian to Jalali for specific fields
                if field in ['submit_date', 'deposit_date'] and value:
                    try:
                        g_date = deposit.submit_date if field == 'submit_date' else deposit.deposit_date
                        if g_date:
                            jdate = jdatetime.datetime.fromgregorian(datetime=g_date)
                            value = jdate.strftime('%Y/%m/%d %H:%M')
                    except Exception:
                        pass

                # Add comma separators for numeric fields
                if field in ['receive_amount', 'pay_amount'] and isinstance(value, (int, float)):
                    value = f"{value:,}"

                # Default clean-up
                if not value:
                    value = '-'
                row.append(str(value))
            rows.append(row)
        return ExcelHandler.generate_excel(headers, rows, file_name='deposit.xlsx', check_field=str(check_field))


@extend_schema(tags=['Financial'])
class OfflineBankAccountViewSet(CustomMixinModelViewSet):
    """
    MEH: Bank Account Model viewset (Offline)
    """
    queryset = BankAccount.objects.all().filter(is_online=False)
    serializer_class = BankAccountSerializer
    filter_backends = [
        filters.OrderingFilter
    ]
    ordering_fields = ['title', 'is_active', 'sort_number']
    permission_classes = [ApiAccess]
    required_api_keys = {
        '__all__': ['offline_bank_account_list'],
        'create': ['create_offline_bank_account'],
        'choice_list': ['allow_any']
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return BankAccountBriefSerializer
        return super().get_serializer_class()

    @extend_schema(summary='Choice list for drop down input')
    @action(detail=False, methods=['get'], serializer_class=BankAccountBriefSerializer,
            url_path='choice-list')
    def choice_list(self, request):
        """
        MEH: List of Bank (offline) for dropdown Menu
        """
        bank_list = BankAccount.objects.filter(is_online=False, is_active=True)
        return self.custom_get(bank_list)


@extend_schema(tags=['Financial'])
class OnlineBankAccountViewSet(OfflineBankAccountViewSet):
    """
    MEH: Bank Account Model viewset (Online)
    """
    queryset = BankAccount.objects.all().filter(is_online=True)
    required_api_keys = {
        '__all__': ['online_bank_account_list'],
        'create': ['create_online_bank_account']
    }

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
    required_api_keys = {
        '__all__': ['cash_back_manager']
    }


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
    required_api_keys = {
        '__all__': ['cash_back_manager']
    }

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
