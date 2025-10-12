from django.db import models
from django.core import validators
from django.utils import timezone
from user.models import User, Role
from employee.models import Employee
from order.models import Order, Cart, OrderStatusRole
from product.models import ProductCategory
from city.models import City, Province
import jdatetime
from jsonschema.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied


class Company(models.Model):
    name = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                            blank=False, null=False)
    agent = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, null=False,
                                 related_name='company')
    national_number = models.CharField(max_length=11, unique=True,
                                       blank=False, null=False, verbose_name='National number')
    economic_number = models.CharField(max_length=11, unique=True,
                                       blank=False, null=False, verbose_name='Economic number')
    registry_number = models.CharField(max_length=11, unique=True,
                                       blank=False, null=False, verbose_name='Registry Number')
    postal_code = models.CharField(max_length=10, validators=[validators.MinLengthValidator(10)],
                                   blank=False, null=False, verbose_name='Postal Code')
    province = models.ForeignKey(Province, on_delete=models.PROTECT,
                                 blank=False, null=False)
    city = models.ForeignKey(City, on_delete=models.PROTECT,
                             blank=False, null=False)
    address_content = models.TextField(blank=False, null=False, verbose_name='Address Content')
    phone_number = models.CharField(max_length=12,
                                    blank=False, null=False, verbose_name='Phone Number')
    accounting_id = models.PositiveBigIntegerField(blank=True, null=True, verbose_name='Accounting ID')

    class Meta:
        ordering = ['agent']
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return f'{self.name}'


class Credit(models.Model):
    total_amount = models.BigIntegerField(default=0,
                                          blank=False, null=False, verbose_name='Total Amount')
    last_update = models.DateTimeField(auto_now=True,
                                       blank=False, null=False, verbose_name='Last Update')
    owner = models.OneToOneField(User, on_delete=models.CASCADE,
                                 blank=False, null=False,
                                 related_name='credit')

    class Meta:
        ordering = ['total_amount', 'id']
        verbose_name = 'Credit'
        verbose_name_plural = 'Credits'

    def __str__(self):
        return f'Credit For: {self.owner}'

    def update_total_amount(self, value):
        self.total_amount += value
        self.save(update_fields=['total_amount'])
    
    def validate_total_amount(self):
        deposit_list = self.deposit_list.all()
        value = 0
        for deposit in deposit_list:
            if deposit.income:
                value += deposit.total_price
            else:
                value -= deposit.total_price
        self.total_amount = value
        self.save(update_fields=['total_amount'])


class DepositConfirmStatus(models.TextChoices):
    CONFIRMED = 'CON', 'تایید شده'
    REJECT = 'REJ', 'تایید نشده'
    PENDING = 'PEN', 'بررسی نشده'
    AUTO = 'AUT', 'تایید خودکار'

class OnlineDepositStatus(models.TextChoices):
    START = 'STR', 'موفق'
    REQUEST = 'REQ', 'ارتباط با بانک'
    SUCCESS = 'SUC', 'موفق'
    FAILURE = 'FAL', 'ناموفق'
    CANCELLED = 'CAN', 'لغو شده'
    UNMATCHED = 'UNM', 'مغایرت'

class DepositType(models.TextChoices):
    WEBSITE = 'WEB', 'ثبت سفارش آنلاین'
    IN_PERSON_SUBMIT= 'PER', 'ثبت سفارش حضوری'
    PLEDGE = 'PLG', 'بیعانه'
    DELIVERY = 'DEL', 'هزینه ارسال'
    PAY = 'PAT', 'بازگشت وجه'
    DAMAGE = 'DMG', 'خسارت'
    CASHBACK = 'BAK', 'سود اعتبار'
    FREE_DISCOUNT = 'DIS', 'تخفیف دستی'
    CODE_DISCOUNT = 'COD', 'کد تخفیف'
    FESTIVAL_DISCOUNT = 'FSD', 'تخفیف جشنواره'
    FESTIVAL_CREDIT = 'FSC', 'اعتبار جشنواره'
    CANCELLED = 'CAN', 'لفو سفارش'
    MANUAL_CREDIT = 'INC', 'اعتبار دستی'

class TransactionType(models.TextChoices):
    ONLINE = 'ONL', 'درگاه پرداخت آنلاین'
    CARD = 'CRD', 'کارت به کارت'
    CASH =  'CSH', 'نقد'
    POS = 'POS', 'کارتخوان'
    DRAFT = 'DRF', 'حواله'
    CHECK = 'CHE', 'چک'
    CREDIT = 'CRE', 'اعتبار'
    DISCOUNT = 'DIS', 'تخفیف'

def deposit_picture_upload_path(instance, filename): # MEH: Store picture in media in deposit folder (it's not in file manager!)
    return f'deposit/{instance.user.id}/{instance.deposit_date.strftime('%Y%m%d%H%M%S')}.jpg'


class Deposit(models.Model):
    total_price = models.PositiveBigIntegerField(blank=False, null=False, verbose_name='Total Price')
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE,
                               blank=False, null=False, related_name='deposit_list')
    submit_date = models.DateTimeField(auto_now_add=True,
                                       blank=False, null=False, verbose_name='Submit Date')
    submit_by = models.ForeignKey(Employee, on_delete=models.PROTECT,
                                  blank=True, null=True, verbose_name='Submit By',
                                  related_name='deposit_submit_list')
    deposit_date = models.DateTimeField(blank=True, null=True, verbose_name='Deposit Date')
    income = models.BooleanField(default=True, blank=False, null=False)
    official_invoice = models.BooleanField(default=False,
                                           blank=False, null=False, verbose_name='Official Invoice')
    transaction_type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                        choices=TransactionType.choices)
    deposit_type = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                    choices=DepositType.choices)
    confirm_status = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                      choices=DepositConfirmStatus.choices, default=DepositConfirmStatus.PENDING,
                                      verbose_name='Confirm Status')
    confirm_by = models.ForeignKey(Employee, on_delete=models.PROTECT,
                                   blank=True, null=True, verbose_name='Confirm By',
                                   related_name='deposit_confirm_list')
    description = models.TextField(max_length=254,
                                   blank=False, null=False)
    tracking_code = models.CharField(max_length=25,
                                     blank=True, null=True, verbose_name="Tracking Code")
    info = models.JSONField(default=dict, blank=True, null=True)
    steps = models.JSONField(default=dict, blank=True, null=True)
    online_status = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                                     choices=OnlineDepositStatus.choices,
                                     blank=True, null=True, verbose_name='Online Status')
    bank = models.ForeignKey('BankAccount', on_delete=models.SET_NULL,
                             blank=True, null=True,
                             related_name='bank_deposit_list')
    picture = models.ImageField(upload_to=deposit_picture_upload_path, blank=True, null=True)

    class Meta:
        ordering = ['-submit_date']
        verbose_name = 'Deposit'
        verbose_name_plural = 'Deposits'

    def __str__(self):
        if self.income:
            return f'Deposit {self.total_price} /Income From: {self.credit.owner}'
        else:
            return f'Deposit {self.total_price} /Pay For: {self.credit.owner}'

    def save(self, *args, **kwargs):
        if not self.deposit_date:
            self.deposit_date = self.submit_date
        super().save(*args, **kwargs)

    def display_price(self):
        if not self.income:
            return self.total_price * -1
        return self.total_price


class CashBackPercent(models.Model):
    percent = models.FloatField(blank=False, null=False)
    min_amount = models.BigIntegerField(blank=False, null=False, verbose_name='Min Amount')
    max_amount = models.BigIntegerField(blank=False, null=False, verbose_name='Max Amount')

    class Meta:
        ordering = ['percent']
        verbose_name = 'Cash Back Percent'
        verbose_name_plural = 'Cash Back Percents'

    def __str__(self):
        return f'Cash Back Percent: #{self.percent}'


class CashBack(models.Model):
    tmp_cashback = models.PositiveIntegerField(default=0,
                                               blank=False, null=False, verbose_name='Tmp Cashback')
    tmp_total_order_amount = models.BigIntegerField(default=0,
                                                    blank=False, null=False, verbose_name='Tmp Total Order Amount')
    now_cashback = models.PositiveIntegerField(default=0,
                                               blank=False, null=False, verbose_name='Now Cashback')
    now_total_order_amount = models.BigIntegerField(default=0,
                                                    blank=False, null=False, verbose_name='Now Total Order Amount')
    manual_percent = models.FloatField(default=0,
                                       blank=False, null=False, verbose_name='Manual Percent')
    credit = models.OneToOneField('Credit', on_delete=models.CASCADE,
                                  blank=False, null=False,
                                  related_name='cashback')
    valid_category = models.ManyToManyField(ProductCategory, blank=True, verbose_name='Valid Category',
                                            related_name='in_cashback')
    history = models.JSONField(default=dict, blank=True, null=True)
    is_active = models.BooleanField(default=False,
                                    blank=False, null=False, verbose_name='Is Active')
    last_confirm = models.BooleanField(default=False,
                                       blank=False, null=False, verbose_name='Last Confirm')

    class Meta:
        verbose_name = 'Cash Back'
        verbose_name_plural = 'Cash Backs'

    def __str__(self):
        return f'Cash Back For: {self.credit.owner}'

    def now_percent(self, old=False):
        if old:
            if self.tmp_total_order_amount > 0:
                return round((self.tmp_cashback / self.tmp_total_order_amount) * 100, 2)
            return 0
        if self.now_total_order_amount > 0:
            return round((self.now_cashback / self.now_total_order_amount) * 100, 2)
        return 0

    def calculate_cashback(self, order): # MEH: Auto run each tima an order submit or canceled
        if order.product.parent_category in self.valid_category or not self.valid_category.exists(): # MEH: Just valid category (Empty means all)
            jalali_now = jdatetime.datetime.fromgregorian(datetime=timezone.now())
            order_jalali_date = jdatetime.datetime.fromgregorian(datetime=order.submit_date)
            if jalali_now.month == order_jalali_date.month: # MEH: Same month (NOW)
                if order.status.role == OrderStatusRole.CANCEL:
                    self.now_total_order_amount -= order.total_price
                else:
                    self.now_total_order_amount += order.total_price
                percent = self.manual_percent
                if not percent:
                    percent_list = CashBackPercent.objects.filter(min_amount__lte=self.now_total_order_amount,
                                                                  min_amount__gt=self.now_total_order_amount)
                    if percent_list.exists():
                        percent = percent_list.first().percent
                self.now_cashback = self.now_total_order_amount * percent / 100
            else:
                pre_month = jalali_now.month - 1 # MEH: Previous month (-1) Means 1 order canceled!
                if pre_month == 0:
                    pre_month = 12
                if pre_month == order_jalali_date.month: # MEH: Make sure its for previous month
                    self.tmp_total_order_amount -= order.total_price
                    percent = self.manual_percent
                    if not percent:
                        percent_list = CashBackPercent.objects.filter(min_amount__lte=self.tmp_total_order_amount,
                                                                      min_amount__gt=self.tmp_total_order_amount)
                        if percent_list.exists():
                            percent = percent_list.first().percent
                    self.tmp_cashback = self.tmp_total_order_amount * percent / 100
                    self.set_cashback_in_history(reset=True) # Manually update history
            self.save()
        pass

    def set_cashback_in_history(self, reset=False): # Auto run in celery beat task every month to set history (confirm = false)
        jalali_now = jdatetime.datetime.fromgregorian(datetime=timezone.now())
        history_date = jalali_now.replace(day=1) - jdatetime.timedelta(days=1)
        history_year = history_date.year
        history_month = history_date.month
        key = f"{history_year}-{history_month:02}"
        if not reset:
            if self.history is None:
                self.history = {}
            self.history[key] = {
                "year": history_year,
                "month": history_month,
                "cashback": self.now_cashback,
                "total_order_amount": self.now_total_order_amount,
                "percent": self.now_percent(),
                "confirm": False
            }
            self.tmp_cashback = self.now_cashback
            self.tmp_total_order_amount = self.now_total_order_amount
            self.now_total_order_amount = 0
            self.now_cashback = 0
            self.last_confirm = False
        else:
            self.history[key]["cashback"] = self.tmp_cashback
            self.history[key]["total_order_amount"] = self.tmp_total_order_amount
            self.history[key]["percent"] = self.now_percent(old=True)
        self.save()

    def confirm_cashback(self, employee): # MEH: To confirm manually last history, then increase user credit (create deposit)
        jalali_now = jdatetime.datetime.fromgregorian(datetime=timezone.now())
        history_date = jalali_now.replace(day=1) - jdatetime.timedelta(days=1) # MEH: Previous month
        history_year = history_date.year
        history_month = history_date.month
        key = f"{history_year}-{history_month:02}" # MEH: Like : 1404-11
        if key not in self.history:# MEH: Just for make sure
            raise ValidationError("Cashback for this period is not prepared yet.")
        if self.history[key]["confirm"]: # MEH: Make sure, if already true, don't continue
            self.last_confirm = True
            self.save(update_fields=["last_confirm"])
            return 0
        if not self.is_active:
            raise PermissionDenied("CashBack deactivate!")
        self.history[key]["cashback"] = self.tmp_cashback
        self.history[key]["total_order_amount"] = self.tmp_total_order_amount
        self.history[key]["percent"] = self.now_percent(old=True)
        self.history[key]["confirm"] = True
        self.last_confirm = True
        Deposit.objects.create(
            total_price=self.tmp_cashback,
            credit=self.credit,
            submit_by=employee,
            deposit_date=timezone.now(),
            income=True,
            transaction_type=TransactionType.CREDIT,
            deposit_type=DepositType.CASHBACK,
            confirm_status=DepositConfirmStatus.AUTO,
            description=f' بازگشت سود اعتبار{key} کاربر {str(self.credit.owner)}',
            tracking_code=f'{self.credit.owner.id}-{key}'
        )
        self.credit.update_total_amount(value=self.tmp_cashback)
        value = self.tmp_cashback
        self.tmp_cashback = 0
        self.tmp_total_order_amount = 0
        self.save()
        return value


class BankAccount(models.Model):
    id = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                          primary_key=True, blank=False, null=False)
    title = models.CharField(max_length=78,
                             blank=False, null=False)
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    is_online = models.BooleanField(default=False,
                                    blank=False, null=False, verbose_name='Is Online')
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
    detail = models.JSONField(default=dict, blank=True, null=True)
    official_invoice = models.BooleanField(default=False,
                                           blank=False, null=False, verbose_name='Official Invoice')

    class Meta:
        ordering = ['-sort_number']
        verbose_name = 'Bank Account'
        verbose_name_plural = 'Bank Accounts'

    def __str__(self):
        if self.is_online:
            return f'Online Bank: {self.title}'
        return f'Offline Bank: {self.title}'


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
