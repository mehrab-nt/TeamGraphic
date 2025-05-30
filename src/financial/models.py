from django.db import models
from django.utils import timezone
from django.core import validators
from django.contrib.auth.models import User
from users.models import Employee, Role
from orders.models import Order, Cart
from products.models import ProductCategory


class Company(models.Model):
    name = models.CharField(max_length=25, blank=False, null=False, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True,
                                related_name='user_company')
    national_number = models.CharField(max_length=11, unique=True, blank=True, null=True, verbose_name='National number')
    economic_number = models.CharField(max_length=11, unique=True, blank=True, null=True, verbose_name='Economic number')
    reg_number = models.CharField(max_length=11, unique=True, blank=True, null=True, verbose_name='Reg Number')
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='Postal Code')
    state = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    address_content = models.TextField(blank=True, null=True, verbose_name='Address Content')
    phone_number = models.CharField(max_length=12, blank=True, null=True, verbose_name='Phone Number')
    accounting_id = models.PositiveBigIntegerField(blank=False, null=False, verbose_name='Accounting ID')

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return f"Company: {self.name}"


class Credit(models.Model):
    total_amount = models.BigIntegerField(blank=False, null=False, verbose_name='Total Amount')
    total_coin = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Coin')
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True,
                                related_name='user_credit')

    class Meta:
        verbose_name = 'Credit'
        verbose_name_plural = 'Credits'

    def __str__(self):
        return f"Credit: {self.user}"


class TurnOver(models.Model):
    credit = models.ForeignKey('Credit', on_delete=models.PROTECT, blank=False, null=False,
                               related_name='turn_over_list')
    deposit = models.OneToOneField('Deposit', on_delete=models.PROTECT, blank=False, null=False,
                                   related_name='for_turn_over')
    now_amount = models.BigIntegerField(blank=False, null=False, verbose_name='Now Amount')

    class Meta:
        ordering = ['-deposit']
        verbose_name = 'Turn Over'
        verbose_name_plural = 'Turn Overs'

    def __str__(self):
        return f"Turn Over: {self.credit.user}"


class CoinStatus(models.TextChoices):
    ACTIVE = 'فعال'
    EXPIRED = 'منقضی'
    USED = 'استفاده شده'


class Coin(models.Model):
    base_coin_amount = models.IntegerField(blank=False, null=False, verbose_name='Base Coin Amount')
    now_coin_amount = models.IntegerField(blank=False, null=False, verbose_name='Now Coin Amount')
    description = models.TextField(blank=False, null=False)
    reg_date = models.DateField(default=timezone.now, blank=False, null=False, verbose_name='Reg Date')
    exp_date = models.DateField(blank=False, null=False, verbose_name='Exp Date')
    status = models.CharField(max_length=12, choices=CoinStatus.choices, default=CoinStatus.ACTIVE,
                              blank=False, null=False)
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, blank=False, null=False,
                               related_name='coin_list')

    class Meta:
        verbose_name = 'Coin'
        verbose_name_plural = 'Coins'

    def __str__(self):
        return f"Coin #{self.base_coin_amount} for {self.credit}"


class CashBack(models.Model):
    tmp_cashback = models.PositiveIntegerField(blank=False, null=False, verbose_name='Tmp Cashback')
    cashback = models.PositiveIntegerField(blank=False, null=False)
    percent = models.FloatField(blank=False, null=False)
    credit = models.OneToOneField('Credit', on_delete=models.PROTECT, blank=False, null=False,
                                  related_name='cashback')

    class Meta:
        verbose_name = 'Cash Back'
        verbose_name_plural = 'Cash Backs'

    def __str__(self):
        return f"Cash Back #{self.tmp_cashback}: {self.credit.user}"


class DepositType(models.TextChoices):
    ONLINE = "پرداخت آنلاین"
    CARD = "کارت به کارت"
    CASH = "نقد"
    POS = "کارتخوان"
    ONLINE_SUBMIT = "ثبت سفارش آنلاین"
    IN_PERSON_SUBMIT= "ثبت سفارش حضوری"
    DELIVERY = "هزینه ارسال"
    PAY = "بازگشت وجه"
    CASHBACK = "سود اعتبار"
    FREE_DISCOUNT = "تخفیف دستی"
    CODE_DISCOUNT = "کد تخفیف"
    FESTIVAL_DISCOUNT = "تخفیف جشنواره"
    FESTIVAL_CREDIT = "اعتبار جشنواره"
    NOT_YET = "پیش فاکتور"
    CANCELLED = "لفو سفارش"


class Deposit(models.Model):
    total_price = models.PositiveIntegerField(blank=False, null=False, verbose_name='Total Price')
    submit_date = models.DateField(default=timezone.now, blank=False, null=False, verbose_name='Submit Date')
    submit_by = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True, verbose_name='Submit By',
                                  related_name='deposit_submit_list')
    deposit_date = models.DateField(blank=True, null=True, verbose_name='Deposit Date')
    income = models.BooleanField(default=True, blank=False, null=False)
    type = models.CharField(max_length=16, choices=DepositType.choices, default=DepositType.ONLINE)
    confirmed = models.BooleanField(default=False, blank=False, null=False)
    confirmed_by = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True, verbose_name='Confirmed By',
                                     related_name='deposit_confirmed_list')
    description = models.TextField(max_length=100, blank=False, null=False)
    tracking_code = models.CharField(max_length=30, blank=True, null=True, verbose_name="Tracking Code")
    steps = models.JSONField(default=dict, blank=False, null=False)
    cart = models.ForeignKey(Cart, on_delete=models.PROTECT, blank=True, null=True, related_name='cart_deposit_list')
    order = models.OneToOneField(Order, on_delete=models.PROTECT, blank=True, null=True, related_name='order_deposit')

    class Meta:
        ordering = ['-submit_date']
        verbose_name = 'Deposit'
        verbose_name_plural = 'Deposits'

    def __str__(self):
        return f"Deposit {self.total_price} from {self.for_turn_over.credit.user}"


class OfflineBankAccount(models.Model):
    title = models.CharField(max_length=37, blank=False, null=False)
    description = models.TextField(max_length=300, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=False, null=False ,verbose_name='Is Active')
    sort_number = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name='Sort Number')
    card_number = models.CharField(max_length=16, validators=[validators.MinLengthValidator(16)], blank=False, null=False,
                                   verbose_name='Card Number')
    bank_account_number = models.CharField(max_length=16, blank=True, null=True, verbose_name='Bank Account Number')
    accounting_id = models.PositiveBigIntegerField(blank=False, null=False, verbose_name="Accounting ID")

    class Meta:
        ordering = ['-sort_number']
        verbose_name = 'Offline Bank Account'
        verbose_name_plural = 'Offline Bank Accounts'

    def __str__(self):
        return f"Bank: {self.title}"


class OnlinePaymentModule(models.Model):
    title = models.CharField(max_length=37, blank=False, null=False)
    sort_number = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name='Sort Number')
    is_active = models.BooleanField(default=True, blank=False, null=False ,verbose_name='Is Active')
    accounting_id = models.PositiveBigIntegerField(blank=False, null=False, verbose_name="Accounting ID")
    detail = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        ordering = ['-sort_number']
        verbose_name = 'Online Payment Module'
        verbose_name_plural = 'Online Payment Modules'

    def __str__(self):
        return f"{self.title}"


class DiscountAmountType(models.TextChoices):
    PERCENT = "درصدی"
    FIX = "ثابت"


class DiscountType(models.TextChoices):
    ONE_TIME = "فقط یک بار"
    ONE_PER_USER = "هر مشتری یک بار"
    FREE = "نا محدود"
    FIRST_TIME = "اولین خرید"


class Discount(models.Model):
    code = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                            blank=False, null=False)
    amount_type = models.CharField(max_length=5, choices=DiscountAmountType.choices, default=DiscountAmountType.PERCENT,
                            blank=False, null=False, verbose_name="Amount Type")
    amount = models.FloatField(blank=False, null=False)
    max_discount_price = models.PositiveIntegerField(blank=True, null=True, verbose_name='Max Discount Price')
    min_order_price = models.PositiveIntegerField(blank=True, null=True, verbose_name='Min Order Price')
    discount_type = models.CharField(max_length=15, choices=DiscountType.choices, default=DiscountType.FREE,
                                     blank=False, null=False, verbose_name='Discount Type')
    last_date = models.DateTimeField(blank=True, null=True, verbose_name='Last Date')
    max_use = models.PositiveIntegerField(blank=True, null=True, verbose_name='Max Use')
    is_active = models.BooleanField(default=True, blank=False, null=False, verbose_name='Is Active')
    description = models.TextField(max_length=300, blank=False, null=False)
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
        ordering = ['-last_date']
        verbose_name = 'Discount'
        verbose_name_plural = 'Discounts'

    def __str__(self):
        return f"{self.code}"


class RoleDiscount(models.Model):
    role = models.ForeignKey(Role, on_delete=models.PROTECT,
                             related_name='all_discounts')
    discount = models.ForeignKey("Discount", on_delete=models.PROTECT,
                                 related_name='all_roles')

    class Meta:
        ordering = ['discount']
        verbose_name = 'Role Discount'
        verbose_name_plural = 'Role Discounts'

    def __str__(self):
        return f"{self.discount} for {self.role}"


class ProductCategoryDiscount(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT,
                                 related_name='all_discounts')
    discount = models.ForeignKey("Discount", on_delete=models.PROTECT,
                                 related_name='all_categories')

    class Meta:
        ordering = ['discount']
        verbose_name = 'Product Category Discount'
        verbose_name_plural = 'Product Category Discounts'

    def __str__(self):
        return f"{self.discount} for {self.category}"


class DiscountUsed(models.Model):
    discount = models.ForeignKey("Discount", on_delete=models.PROTECT, blank=False, null=False,
                                 related_name='discount_used')
    amount = models.PositiveIntegerField(blank=False, null=False)
    order = models.OneToOneField(Order, on_delete=models.PROTECT, blank=False, null=False,
                                 related_name='order_discount')

    class Meta:
        ordering = ['order']
        verbose_name = 'Discount Used'
        verbose_name_plural = 'Discounts Used'

    def __str__(self):
        return f"{self.discount} used for {self.order}"


class FestivalType(models.TextChoices):
    DISCOUNT = "تخفیف"
    CREDIT = "اعتبار"


class Festival(models.Model):
    title = models.CharField(max_length=37, validators=[validators.MinLengthValidator(3)], blank=False, null=False)
    start_date = models.DateTimeField(blank=False, null=False, verbose_name='Start Date')
    end_date = models.DateTimeField(blank=False, null=False, verbose_name='End Date')
    type = models.CharField(max_length=7, choices=FestivalType.choices, default=FestivalType.DISCOUNT)
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
        ordering = ['-start_date']
        verbose_name = 'Festival'
        verbose_name_plural = 'Festivals'

    def __str__(self):
        return f"{self.title}"


class RoleFestival(models.Model):
    role = models.ForeignKey(Role, on_delete=models.PROTECT,
                             related_name='all_festivals')
    festival = models.ForeignKey('Festival', on_delete=models.PROTECT,
                                 related_name='all_roles')

    class Meta:
        ordering = ['festival']
        verbose_name = 'Role Festival'
        verbose_name_plural = 'Role Festivals'

    def __str__(self):
        return f"{self.festival} for {self.role}"


class ProductCategoryFestival(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT,
                                 related_name='all_festivals')
    festival = models.ForeignKey("Festival", on_delete=models.PROTECT,
                                 related_name='all_categories')
    amount_type = models.CharField(max_length=5, choices=DiscountAmountType.choices, default=DiscountAmountType.PERCENT,
                            blank=False, null=False, verbose_name="Amount Type")
    amount = models.FloatField(blank=False, null=False)

    class Meta:
        ordering = ['festival']
        verbose_name = 'Product Category Festival'
        verbose_name_plural = 'Product Category Festivals'

    def __str__(self):
        return f"{self.festival} for {self.category}"


class FestivalUsed(models.Model):
    festival = models.ForeignKey("Festival", on_delete=models.PROTECT, blank=False, null=False,
                                 related_name='festival_used')
    amount = models.PositiveIntegerField(blank=False, null=False)
    order = models.OneToOneField(Order, on_delete=models.PROTECT, blank=False, null=False,
                                 related_name='order_festival')

    class Meta:
        ordering = ['order']
        verbose_name = 'Festival Used'
        verbose_name_plural = 'Festivals Used'

    def __str__(self):
        return f"{self.festival} used for {self.order}"
