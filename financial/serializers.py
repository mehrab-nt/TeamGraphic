from rest_framework import serializers
from .filters import DepositFilter
from .models import Deposit, TransactionType, DepositType, DepositConfirmStatus, Company, Credit, BankAccount, \
    CashBackPercent, CashBack
from user.models import User
from api.mixins import CustomModelSerializer, CustomChoiceField
from api.responses import *
from rest_framework.pagination import PageNumberPagination


class CompanySerializer(CustomModelSerializer):
    """
    MEH: Company full information
    """
    agent = serializers.PrimaryKeyRelatedField(queryset=User.objects.all().filter(is_active=True, is_employee=False))
    agent_display = serializers.StringRelatedField(source='agent')
    city_display = serializers.StringRelatedField(source='city')
    province_display = serializers.StringRelatedField(source='province')

    class Meta:
        model = Company
        fields = '__all__'

    def to_representation(self, instance): # MEH: Can not update agent user anymore (only delete)
        data = super().to_representation(instance)
        if self.context.get('view').action in ['update', 'partial_update']:
            data.pop('agent', None)
        return data


class DepositSerializer(CustomModelSerializer):
    """
    MEH: Deposit Full information
    """
    user = serializers.SerializerMethodField()
    user_display = serializers.SerializerMethodField()
    submit_by_display = serializers.StringRelatedField(source='submit_by')
    confirm_by_display = serializers.StringRelatedField(source='confirm_by')
    total_price = serializers.SerializerMethodField()
    deposit_type_display = serializers.SerializerMethodField()
    transaction_type_display = serializers.SerializerMethodField()
    confirm_status_display = serializers.SerializerMethodField()
    bank_display = serializers.StringRelatedField(source='bank')

    class Meta:
        model = Deposit
        fields = '__all__'

    @staticmethod
    def get_user(obj):
        return obj.credit.owner.id

    @staticmethod
    def get_user_display(obj):
        return str(obj.credit.owner)

    @staticmethod
    def get_total_price(obj):
        if not obj.income:
            return obj.total_price * -1
        return obj.total_price

    @staticmethod
    def get_deposit_type_display(obj):
        return obj.get_deposit_type_display()

    @staticmethod
    def get_transaction_type_display(obj):
        return obj.get_transaction_type_display()

    @staticmethod
    def get_confirm_status_display(obj):
        return obj.get_confirm_status_display()


class DepositBriefListSerializer(DepositSerializer):
    """
    MEH: brief Deposit Information for list
    """
    class Meta:
        model = Deposit
        fields = ['id', 'submit_date', 'user', 'user_display', 'total_price', 'deposit_type', 'deposit_type_display',
                  'transaction_type', 'transaction_type_display', 'deposit_date',
                  'submit_by', 'submit_by_display', 'confirm_by', 'confirm_by_display', 'description']


class DepositPendingListSerializer(DepositSerializer):
    """
    MEH: Deposit Pending for confirm list Information
    """
    class Meta:
        model = Deposit
        fields = ['id', 'submit_date', 'user_display', 'total_price', 'deposit_type', 'deposit_type_display',
                  'transaction_type', 'transaction_type_display', 'deposit_date',
                  'confirm_status', 'confirm_status_display', 'submit_by_display', 'description', 'tracking_code', 'bank_display']


class DepositPendingSetStatusSerializer(CustomModelSerializer):
    """
    MEH: Deposit Pending for update confirm status (Confirm or Reject)
    with optional description
    """
    confirm_status = CustomChoiceField(choices=[
        (DepositConfirmStatus.CONFIRMED, DepositConfirmStatus.CONFIRMED.label),
        (DepositConfirmStatus.REJECT, DepositConfirmStatus.REJECT.label)
    ])
    description = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Deposit
        fields = ['confirm_status', 'description']

    def validate(self, attrs):
        if not attrs['description']: # MEH: if description is empty, drop to keep old description in update
            attrs.pop('description')
        return attrs

    def update(self, instance, validated_data):
        deposit = super().update(instance, validated_data)
        if deposit.confirm_status == DepositConfirmStatus.CONFIRMED:
            deposit.credit.update_total_amount(deposit.display_price())
        return deposit


class DepositCreateSerializer(CustomModelSerializer):
    """
    MEH: Deposit Submit Information
    """
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all().filter(is_active=True, is_employee=False))

    transaction_type = CustomChoiceField(choices=[
        (TransactionType.CARD, TransactionType.CARD.label),
        (TransactionType.CASH, TransactionType.CASH.label),
        (TransactionType.POS, TransactionType.POS.label),
        (TransactionType.DRAFT, TransactionType.DRAFT.label),
        (TransactionType.CHECK, TransactionType.CHECK.label),
        (TransactionType.CREDIT, TransactionType.CREDIT.label)
    ])
    deposit_type = CustomChoiceField(choices=[
        (DepositType.PLEDGE, DepositType.PLEDGE.label),
        (DepositType.PAY, DepositType.PAY.label),
        (DepositType.DAMAGE, DepositType.DAMAGE.label),
        (DepositType.MANUAL_CREDIT, DepositType.MANUAL_CREDIT.label)
    ])
    confirm_status = CustomChoiceField(choices=[
        (DepositConfirmStatus.PENDING, DepositConfirmStatus.PENDING.label),
        (DepositConfirmStatus.CONFIRMED, DepositConfirmStatus.AUTO.label)
    ])

    class Meta:
        model = Deposit
        fields = ['user', 'total_price', 'income', 'deposit_date', 'transaction_type', 'deposit_type',
                  'bank', 'description', 'confirm_status', 'info']

    def create(self, validated_data):
        user = validated_data.pop('user')
        validated_data['credit'] = user.credit
        return super().create(validated_data)


class DepositCreateInPersonSerializer(DepositCreateSerializer):
    """
    MEH: Deposit Submit Information for In Person submit customer Cart,
    Use in Cart viewset
    # todo: handle in Cart viewset (post list of deposit) and set deposit_type auto = IN_PERSON_SUBMIT & Confirm_staus = PENDING
    """
    transaction_type = CustomChoiceField(choices=[
        (TransactionType.CARD, TransactionType.CARD.label),
        (TransactionType.CASH, TransactionType.CASH.label),
        (TransactionType.POS, TransactionType.POS.label),
        (TransactionType.DRAFT, TransactionType.DRAFT.label),
        (TransactionType.CREDIT, TransactionType.CREDIT.label),
        (TransactionType.DISCOUNT, TransactionType.DISCOUNT.label)
    ])

    class Meta:
        model = Deposit
        fields = ['user', 'total_price', 'deposit_date', 'transaction_type',
                  'bank', 'description', 'picture']


class DepositOnlineDetailSerializer(DepositSerializer):
    """
    MEH: Online Deposit brief list Information
    """
    class Meta:
        model = Deposit
        fields = ['id', 'user', 'user_display', 'total_price', 'online_status', 'deposit_type',
                  'submit_date', 'deposit_date', 'bank', 'tracking_code', 'steps']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context.get('view').action != 'retrieve':  # MEH: Drop steps in other action (list)
            data.pop('steps', None)
        return data


class DepositBriefInfoForUserManualListSerializer(DepositSerializer):
    """
    MEH: Deposit brief info for user manual list (Pending, Confirm, Reject)
    """
    class Meta:
        model = Deposit
        fields = ['id', 'total_price', 'submit_date', 'deposit_date', 'transaction_type_display', 'confirm_status', 'confirm_status_display']


class DepositBriefInfoForCreditSerializer(DepositSerializer):
    """
    MEH: Deposit brief info for User credit report
    """
    class Meta:
        model = Deposit
        fields = ['submit_date', 'description', 'income', 'total_price', 'deposit_type_display', 'transaction_type_display']


class CreditSerializer(CustomModelSerializer):
    """
    MEH: Credit full information
    """
    owner = serializers.StringRelatedField()
    deposit_list = serializers.SerializerMethodField()

    class Meta:
        model = Credit
        fields = '__all__'

    def get_deposit_list(self, obj):
        request = self.context.get('request')
        deposit_list = obj.deposit_list.all().filter(confirm_status=DepositConfirmStatus.CONFIRMED) # MEH: Filter only Confirmed deposit
        filter_qs = DepositFilter(request.GET, queryset=deposit_list).qs # MEH: Filter in request param
        view = self.context.get('view')
        page = view.paginator.paginate_queryset(filter_qs, request, view=view) # MEH: use viewset pagination setting for nested deposit list
        return view.paginator.get_paginated_response(
            DepositBriefInfoForCreditSerializer(page, many=True, context=self.context).data
        ).data


class BankAccountSerializer(CustomModelSerializer):
    """
    MEH: Bank Account full Information (Offline)
    """
    class Meta:
        model = BankAccount
        exclude = ['is_online']


class BankAccountBriefSerializer(BankAccountSerializer):
    """
    MEH: Bank Account Brief Information for list
    """
    class Meta:
        model = BankAccount
        fields = ['id', 'title', 'description', 'is_active']


class CashBackPercentSerializer(CustomModelSerializer):
    """
    MEH: Cash Back Percent full Information
    """
    class Meta:
        model = CashBackPercent
        fields = '__all__'


class CashBackSerializer(CustomModelSerializer):
    """
    MEH: Cash Back full Information
    """
    owner_id = serializers.SerializerMethodField()
    owner_display = serializers.SerializerMethodField()
    now_percent = serializers.SerializerMethodField()

    class Meta:
        model = CashBack
        exclude = ['credit']
        read_only_fields = ['history', 'tmp_cashback', 'tmp_total_order_amount', 'now_cashback', 'now_total_order_amount', 'last_confirm']

    @staticmethod
    def get_owner_id(obj):
        return str(obj.credit.owner.id)

    @staticmethod
    def get_owner_display(obj):
        return str(obj.credit.owner)

    @staticmethod
    def get_now_percent(obj):
        return obj.now_percent()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context.get('view').action == 'list':  # MEH: Drop history in list action
            data.pop('history', None)
        return data
