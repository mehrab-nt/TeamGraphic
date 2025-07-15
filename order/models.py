from django.db import models
from django.core import validators
from django.utils import timezone
from file_manager.models import FileItem
from product.models import Product
from user.models import User
from employee.models import Employee
from delivery.models import DeliveryReceipt


class CartStatus(models.TextChoices):
    CART = 'CRT', 'سبد خرید'
    PAYMENT = 'PAY', 'پرداخت شده'
    CONFIRM = 'CON', 'تأیید مالی'
    END = 'END', 'نهایی شده'


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT,
                             blank=False, null=False,
                             related_name='cart_list')
    create_date = models.DateTimeField(default=timezone.now,
                                       blank=False, null=False, verbose_name='Create Date')
    last_change_date = models.DateTimeField(default=timezone.now,
                                            blank=False, null=False, verbose_name='Last Change Date')
    payment_data = models.DateField(blank=True, null=True, verbose_name='Payment Date')
    status = models.CharField(max_length=3, validators=[validators.MinLengthValidator(3)],
                              choices=CartStatus.choices, default=CartStatus.CART,
                              blank=False, null=False)
    total_price = models.PositiveIntegerField(default=0,
                                              blank=False, null=False, verbose_name='Total Price')

    class Meta:
        ordering = ['-create_date']
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f"Cart #{self.pk}"


class OrderStatusRole(models.TextChoices):
    CART = 'CRT', 'سبد خرید'
    EXCLUSIVE = 'EXC', 'سفارش اختصاصی'
    NEW = 'NEW', 'جدید'
    READY = 'RED', 'آماده تحویل'
    DELIVERED = 'DLI', 'تحویل داده شده'
    CANCEL = 'CAN', 'لغو شده'


class OrderStatus(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    is_active = models.BooleanField(default=True,
                                    blank=False, null=False, verbose_name='Is Active')
    mandatory = models.BooleanField(default=True,
                                    blank=False, null=False)
    sort_number = models.SmallIntegerField(default=0,
                                           blank=False, null=False, verbose_name='Sort Number')
    role = models.CharField(max_length=3, unique=True, validators=[validators.MinLengthValidator(3)],
                            choices=OrderStatusRole,
                            blank=True, null=True)
    custom_style_class = models.CharField(max_length=23,
                                          blank=True, null=True, verbose_name='Custom Style Class')
    employee_access = models.ManyToManyField(
        Employee,
        through='OrderStatusAccess',
        through_fields=('order_status', 'employee'),
        verbose_name='Employee Access'
    )

    class Meta:
        ordering = ['-sort_number']
        verbose_name = 'Order Status'
        verbose_name_plural = 'Order Statuses'

    def __str__(self):
        return f"#{self.sort_number} Order Status: {self.title}"


class OrderStatusAccess(models.Model):
    order_status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE,
                                     verbose_name="Order Status",
                                     related_name='employee_list')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,
                                 related_name='access_order_status_list')

    class Meta:
        verbose_name = 'Order Status Access'
        verbose_name_plural = 'Order Status Accesses'

    def __str__(self):
        return f"{self.order_status} #Access For: {self.employee}"


class Order(models.Model):
    title = models.CharField(max_length=23, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    product = models.ForeignKey(Product, on_delete=models.PROTECT,
                                blank=False, null=False,
                                related_name='order_list')
    # preview = models.ImageField(upload_to="previews/", blank=False, null=False)
    # alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
    #                        blank=False, null=False)
    ready_date = models.DateField(blank=True, null=True, verbose_name='Ready Date')
    description = models.TextField(max_length=236,
                                   blank=True, null=True)
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT,
                               blank=False, null=False,
                               related_name='order_list')
    internal_id = models.PositiveBigIntegerField(blank=True, null=True, verbose_name='Internal ID')
    classify_id = models.PositiveIntegerField(blank=True, null=True, verbose_name='Classify ID')
    cart = models.ForeignKey(Cart, on_delete=models.PROTECT,
                             blank=False, null=False,
                             related_name='order_list')
    product_price = models.PositiveIntegerField(default=0,
                                                blank=False, null=False, verbose_name='Product Price')
    files = models.ManyToManyField(FileItem, blank=True, related_name='for_orders')
    fields = models.JSONField(default=dict,
                              blank=False, null=False)
    options = models.JSONField(default=dict,
                               blank=False, null=False)
    options_price = models.PositiveIntegerField(default=0,
                                                blank=False, null=False, verbose_name='Options Price')
    reports = models.JSONField(default=dict,
                               blank=False, null=False)
    notes = models.JSONField(default=dict,
                             blank=False, null=False)
    saler_employee = models.ForeignKey(Employee, on_delete=models.PROTECT,
                                       blank=True, null=True, verbose_name="Saler Employee",
                                       related_name='sale_order_list')
    delivery_receipt = models.OneToOneField(DeliveryReceipt, on_delete=models.PROTECT,
                                            blank=True, null=True, verbose_name='Delivery Receipt',
                                            related_name='delivery_receipt_for_order')
    delivery_price = models.PositiveIntegerField(default=0,
                                                 blank=False, null=False, verbose_name='Delivery Price')
    total_price = models.PositiveIntegerField(default=0,
                                              blank=False, null=False, verbose_name='Total Price')

    class Meta:
        ordering = ['cart']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order #{self.pk}: {self.title}"
