from django.db import models
from django.core import validators
from django.utils import timezone
from user.models import User, Role
from employee.models import Employee
from order.models import Order, Cart
from product.models import ProductCategory


class Company(models.Model):
    name = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                            blank=False, null=False)
    manager = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='company')
    national_number = models.CharField(max_length=11, unique=True,
                                       blank=True, null=True, verbose_name='National number')
    economic_number = models.CharField(max_length=11, unique=True,
                                       blank=True, null=True, verbose_name='Economic number')
    registry_number = models.CharField(max_length=11, unique=True,
                                       blank=True, null=True, verbose_name='Registry Number')
    postal_code = models.CharField(max_length=10, validators=[validators.MinLengthValidator(10)],
                                   blank=True, null=True, verbose_name='Postal Code')
    state = models.CharField(max_length=23,
                             blank=True, null=True)
    city = models.CharField(max_length=23,
                            blank=True, null=True)
    address_content = models.TextField(blank=True, null=True, verbose_name='Address Content')
    phone_number = models.CharField(max_length=12,
                                    blank=True, null=True, verbose_name='Phone Number')
    accounting_id = models.PositiveBigIntegerField(blank=True, null=True, verbose_name='Accounting ID')

    class Meta:
        ordering = ['manager']
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return f'Company: {self.name}'


class Credit(models.Model):
    total_amount = models.BigIntegerField(blank=False, null=False, verbose_name='Total Amount')
    total_coin = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Coin')
    owner = models.OneToOneField(User, on_delete=models.CASCADE,
                                 blank=False, null=False,
                                 related_name='credit')

    class Meta:
        ordering = ['owner']
        verbose_name = 'Credit'
        verbose_name_plural = 'Credits'

    def __str__(self):
        return f'Credit For: {self.owner}'


class TurnOver(models.Model):
    credit = models.ForeignKey(Credit, on_delete=models.PROTECT,
                               blank=False, null=False,
                               related_name='turn_over_list')
    deposit = models.OneToOneField('Deposit', on_delete=models.PROTECT,
                                   blank=False, null=False,
                                   related_name='turn_over_list')
    result_amount = models.BigIntegerField(blank=False, null=False, verbose_name='Result Amount')

    class Meta:
        ordering = ['deposit', 'credit']
        verbose_name = 'Turn Over'
        verbose_name_plural = 'Turn Overs'

    def __str__(self):
        return f'Turn Over For: {self.credit.owner}'


class CoinStatus(models.TextChoices):
    ACTIVE = 'ACT', 'فعال'
    EXPIRED = 'EXP', 'منقضی'
    USED = 'USE', 'استفاده شده'


class Coin(models.Model):
    base_coin_amount = models.PositiveSmallIntegerField(blank=False, null=False, verbose_name='Base Coin Amount')
    now_coin_amount = models.PositiveSmallIntegerField(blank=False, null=False, verbose_name='Now Coin Amount')
    description = models.TextField(max_length=78,
                                   blank=False, null=False)
    reg_date = models.DateField(default=timezone.now,
                                blank=False, null=False, verbose_name='Reg Date')
    exp_date = models.DateField(blank=False, null=False, verbose_name='Exp Date')
    status = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                              choices=CoinStatus.choices, default=CoinStatus.ACTIVE,
                              blank=False, null=False)
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE,
                               blank=False, null=False,
                               related_name='coin_list')

    class Meta:
        ordering = ['-reg_date', 'credit']
        verbose_name = 'Coin'
        verbose_name_plural = 'Coins'

    def __str__(self):
        return f'Coin #{self.base_coin_amount} /For: {self.credit.owner}'


class CashBackPercent(models.Model):
    percent = models.FloatField(blank=False, null=False)
    min_amount = models.BigIntegerField(blank=False, null=False, verbose_name='Min Amount')
    max_amount = models.BigIntegerField(blank=False, null=False, verbose_name='Max Amount')

    class Meta:
        ordering = ['-percent']
        verbose_name = 'Cash Back Percent'
        verbose_name_plural = 'Cash Back Percents'

    def __str__(self):
        return f'Cash Back Percent: #{self.percent}'


class CashBack(models.Model):
    tmp_cashback = models.PositiveIntegerField(blank=False, null=False, verbose_name='Tmp Cashback')
    total_order_amount = models.BigIntegerField(blank=False, null=False, verbose_name='Total Order Amount')
    percent = models.ForeignKey(CashBackPercent, on_delete=models.PROTECT, blank=False, null=False)
    now_cashback = models.PositiveIntegerField(blank=False, null=False, verbose_name='Now Cashback')
    credit = models.OneToOneField('Credit', on_delete=models.PROTECT,
                                  blank=False, null=False,
                                  related_name='cashback')

    class Meta:
        verbose_name = 'Cash Back'
        verbose_name_plural = 'Cash Backs'

    def __str__(self):
        return f'Cash Back For: {self.credit.owner}'


class DepositType(models.TextChoices):
    ONLINE = 'ONL', 'پرداخت آنلاین'
    CARD = 'CRD', 'کارت به کارت'
    CASH =  'CSH', 'نقد'
    POS = 'POS', 'کارتخوان'
    WEBSITE = 'WEB', 'ثبت سفارش آنلاین'
    IN_PERSON_SUBMIT= 'PER', 'ثبت سفارش حضوری'
    DELIVERY = 'DEL', 'هزینه ارسال'
    PAY = 'PAT', 'بازگشت وجه'
    CASHBACK = 'BAK', 'سود اعتبار'
    FREE_DISCOUNT = 'DIS', 'تخفیف دستی'
    CODE_DISCOUNT = 'COD', 'کد تخفیف'
    FESTIVAL_DISCOUNT = 'FSD', 'تخفیف جشنواره'
    FESTIVAL_CREDIT = 'FSC', 'اعتبار جشنواره'
    PRE_ORDER = 'PRE', 'پیش فاکتور'
    CANCELLED = 'CAN', 'لفو سفارش'


class Deposit(models.Model):
    total_price = models.PositiveBigIntegerField(blank=False, null=False, verbose_name='Total Price')
    submit_date = models.DateField(default=timezone.now,
                                   blank=False, null=False, verbose_name='Submit Date')
    submit_by = models.ForeignKey(Employee, on_delete=models.PROTECT,
                                  blank=True, null=True, verbose_name='Submit By',
                                  related_name='deposit_submit_list')
    deposit_date = models.DateField(blank=True, null=True, verbose_name='Deposit Date')
    income = models.BooleanField(default=True, blank=False, null=False)
    type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                            choices=DepositType.choices)
    confirm = models.BooleanField(default=False, blank=False, null=False)
    confirm_by = models.ForeignKey(Employee, on_delete=models.PROTECT,
                                   blank=True, null=True, verbose_name='Confirm By',
                                   related_name='deposit_confirm_list')
    description = models.TextField(max_length=254,
                                   blank=False, null=False)
    tracking_code = models.CharField(max_length=25,
                                     blank=True, null=True, verbose_name="Tracking Code")
    steps = models.JSONField(default=dict, blank=False, null=False)
    cart = models.ForeignKey(Cart, on_delete=models.PROTECT,
                             blank=True, null=True, related_name='cart_deposit_list')

    class Meta:
        ordering = ['-submit_date']
        verbose_name = 'Deposit'
        verbose_name_plural = 'Deposits'

    def __str__(self):
        if self.income:
            return f'Deposit {self.total_price} /Income From: {self.turn_over_list.credit.owner}'
        else:
            return f'Deposit {self.total_price} /Pay For: {self.turn_over_list.credit.owner}'


class OfflineBankAccount(models.Model):
    title = models.CharField(max_length=78,
                             blank=False, null=False)
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False ,verbose_name='Is Active')
    sort_number = models.PositiveIntegerField(default=0,
                                              blank=False, null=False, verbose_name='Sort Number')
    card_number = models.CharField(max_length=16, validators=[validators.MinLengthValidator(16)],
                                   blank=False, null=False,
                                   verbose_name='Card Number')
    bank_account_number = models.CharField(max_length=16,
                                           blank=True, null=True, verbose_name='Bank Account Number')
    accounting_id = models.PositiveBigIntegerField(blank=True, null=True, verbose_name="Accounting ID")

    class Meta:
        ordering = ['-sort_number']
        verbose_name = 'Offline Bank Account'
        verbose_name_plural = 'Offline Bank Accounts'

    def __str__(self):
        return f'Bank: {self.title}'


class OnlinePaymentModule(models.Model):
    title = models.CharField(max_length=23,
                             blank=False, null=False)
    sort_number = models.PositiveIntegerField(default=0,
                                              blank=False, null=False, verbose_name='Sort Number')
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False ,verbose_name='Is Active')
    accounting_id = models.PositiveBigIntegerField(blank=True, null=True, verbose_name="Accounting ID")
    detail = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        ordering = ['-sort_number']
        verbose_name = 'Online Payment Module'
        verbose_name_plural = 'Online Payment Modules'

    def __str__(self):
        return f'{self.title}'


class DiscountAmountType(models.TextChoices):
    PERCENT = 'PER', 'درصدی'
    FIX = 'FIX', 'ثابت'


class DiscountType(models.TextChoices):
    ONE_TIME = 'ONT', 'فقط یک بار'
    ONE_PER_USER = 'ONU', 'هر مشتری یک بار'
    FREE = 'FRE', 'نا محدود'
    FIRST_TIME = 'FIR', 'اولین خرید'


class Discount(models.Model):
    code = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                            blank=False, null=False)
    amount_type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                   choices=DiscountAmountType.choices, default=DiscountAmountType.PERCENT,
                                   blank=False, null=False, verbose_name='Amount Type')
    amount = models.FloatField(blank=False, null=False)
    max_discount_price = models.PositiveIntegerField(blank=True, null=True, verbose_name='Max Discount Price')
    min_order_price = models.PositiveIntegerField(blank=True, null=True, verbose_name='Min Order Price')
    discount_type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                     choices=DiscountType.choices, default=DiscountType.FREE,
                                     blank=False, null=False, verbose_name='Discount Type')
    reg_date = models.DateTimeField(default=timezone.now,
                                    blank=False, null=False, verbose_name='Reg Date')
    exp_date = models.DateTimeField(blank=True, null=True, verbose_name='Exp Date')
    max_use = models.PositiveIntegerField(blank=True, null=True, verbose_name='Max Use')
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name='Is Active')
    description = models.TextField(max_length=236, blank=False, null=False)
    role = models.ManyToManyField(
        Role,
        through='RoleDiscount',
        through_fields=('discount', 'role'),
    )
    product_category = models.ManyToManyField(
        ProductCategory,
        through='ProductCategoryDiscount',
        through_fields=('discount', 'category')
    )

    class Meta:
        ordering = ['reg_date']
        verbose_name = 'Discount'
        verbose_name_plural = 'Discounts'

    def __str__(self):
        return f'Discount: {self.code}'


class RoleDiscount(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE,
                             related_name='discount_list')
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE,
                                 related_name='role_list')

    class Meta:
        ordering = ['discount', 'role']
        verbose_name = 'Role Discount'
        verbose_name_plural = 'Role Discounts'

    def __str__(self):
        return f'{self.discount} /For: {self.role}'


class ProductCategoryDiscount(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE,
                                 related_name='discount_list')
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE,
                                 related_name='product_category_list')

    class Meta:
        ordering = ['discount', 'category']
        verbose_name = 'Product Category Discount'
        verbose_name_plural = 'Product Category Discounts'

    def __str__(self):
        return f'{self.discount} /For: {self.category}'


class DiscountUsed(models.Model):
    discount = models.ForeignKey(Discount, on_delete=models.PROTECT,
                                 blank=False, null=False,
                                 related_name='used_list')
    amount = models.PositiveIntegerField(blank=False, null=False)
    order = models.OneToOneField(Order, on_delete=models.PROTECT,
                                 blank=False, null=False,
                                 related_name='discount')

    class Meta:
        ordering = ['order']
        verbose_name = 'Discount Used'
        verbose_name_plural = 'Discounts Used'

    def __str__(self):
        return f'{self.discount} /Used For: {self.order}'


class FestivalType(models.TextChoices):
    DISCOUNT = 'DIS', 'تخفیف'
    CREDIT = 'CRE', 'اعتبار'


class Festival(models.Model):
    title = models.CharField(max_length=23, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    reg_date = models.DateTimeField(blank=False, null=False, verbose_name='Reg Date')
    start_date = models.DateTimeField(blank=False, null=False, verbose_name='Start Date')
    exp_date = models.DateTimeField(blank=False, null=False, verbose_name='Exp Date')
    type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                            choices=FestivalType.choices, default=FestivalType.DISCOUNT)
    min_order_price = models.PositiveIntegerField(blank=True, null=True, verbose_name='Min Order Price')
    role = models.ManyToManyField(
        Role,
        through='RoleFestival',
        through_fields=('festival', 'role'),
    )
    product_category = models.ManyToManyField(
        ProductCategory,
        through='ProductCategoryFestival',
        through_fields=('festival', 'category')
    )


    class Meta:
        ordering = ['-reg_date']
        verbose_name = 'Festival'
        verbose_name_plural = 'Festivals'

    def __str__(self):
        return f'Festival: {self.title}'


class RoleFestival(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE,
                             related_name='festival_list')
    festival = models.ForeignKey(Festival, on_delete=models.CASCADE,
                                 related_name='role_list')

    class Meta:
        ordering = ['festival', 'role']
        verbose_name = 'Role Festival'
        verbose_name_plural = 'Role Festivals'

    def __str__(self):
        return f"{self.festival} for {self.role}"


class ProductCategoryFestival(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE,
                                 related_name='festival_list')
    festival = models.ForeignKey(Festival, on_delete=models.CASCADE,
                                 related_name='product_category_list')
    amount_type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                   choices=DiscountAmountType.choices, default=DiscountAmountType.PERCENT,
                                   blank=False, null=False, verbose_name='Amount Type')
    amount = models.FloatField(blank=False, null=False)

    class Meta:
        ordering = ['festival', 'category']
        verbose_name = 'Product Category Festival'
        verbose_name_plural = 'Product Category Festivals'

    def __str__(self):
        return f"{self.festival} for {self.category}"


class FestivalUsed(models.Model):
    festival = models.ForeignKey(Festival, on_delete=models.PROTECT,
                                 blank=False, null=False,
                                 related_name='used_list')
    amount = models.PositiveIntegerField(blank=False, null=False)
    order = models.OneToOneField(Order, on_delete=models.PROTECT,
                                 blank=False, null=False,
                                 related_name='festival')

    class Meta:
        ordering = ['order']
        verbose_name = 'Festival Used'
        verbose_name_plural = 'Festivals Used'

    def __str__(self):
        return f'{self.festival} /Used For: {self.order}'
