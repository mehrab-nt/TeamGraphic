from django.db import models
from django.core import validators
from django.utils import timezone
from products.models import Product
from django.contrib.auth.models import User
from users.models import Employee
from deliveries.models import DeliveryReceipt


class OrderStatusRole(models.TextChoices):
    CART = "CRT"
    NEW = "NEW"
    READY = "RED"
    DELIVERED = "DLI"
    CANCEL = "CAN"
    CUSTOM = "CUS"


class OrderStatus(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    is_active = models.BooleanField(default=True, blank=False, null=False, verbose_name="Is Active")
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name="Sort Number")
    order_status_role = models.CharField(max_length=3, choices=OrderStatusRole, default=OrderStatusRole.CUSTOM, blank=False, null=False, verbose_name="Order Status Role")
    style = models.JSONField(default=dict, blank=False, null=False)
    employee_access = models.ManyToManyField(
        Employee,
        through='OrderStatusAccess',
        through_fields=('order_status', 'employee'),
        verbose_name="Employee Access"
    )

    class Meta:
        ordering = ['-sort_number']
        verbose_name = "Order Status"
        verbose_name_plural = "Order Statuses"

    def __str__(self):
        return f"Order Status: {self.title}"


class OrderStatusAccess(models.Model):
    order_status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, verbose_name="Order Status",
                                     related_name='all_employees')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,
                                 related_name='access_order_statuses')

    class Meta:
        verbose_name = "Order Status Access"
        verbose_name_plural = "Order Status Accesses"

    def __str__(self):
        return f"{self.order_status} - Access for: {self.employee}"


class Order(models.Model):
    title = models.CharField(max_length=23, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, blank=False, null=False,
                                related_name="product_in_orders")
    # preview = models.ImageField(upload_to="previews/", blank=False, null=False)
    alt = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                           blank=False, null=False)
    fields = models.JSONField(default=dict, blank=False, null=False)
    delivery_date = models.DateField(blank=True, null=True, verbose_name="Delivery Date")
    description = models.TextField(max_length=300, blank=True, null=True)
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, blank=False, null=False,
                                     related_name='status_in_orders')
    internal_id = models.PositiveBigIntegerField(blank=True, null=True, verbose_name="Internal ID")
    classify_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="Classify ID")
    cart = models.ForeignKey("Cart", on_delete=models.PROTECT, blank=False, null=False,
                             related_name="order_list")
    product_price = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="Product Price")
    options = models.JSONField(default=dict, blank=False, null=False)
    options_price = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="Options Price")
    reports = models.JSONField(default=dict, blank=False, null=False)
    notes = models.JSONField(default=dict, blank=False, null=False)
    sale_employee = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Sale Employee",
                                      related_name="submit_order_list",)
    delivery_receipt = models.OneToOneField(DeliveryReceipt, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Delivery Receipt",
                                            related_name="delivery_receipt_order")
    delivery_price = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="Delivery Price")
    total_price = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="Total Price")

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order #{self.pk}: {self.title}"


class CartStatus(models.TextChoices):
    CART = "سبد خرید"
    PAYMENT = "پرداخت شده"
    CONFIRM = "تأیید مالی"
    END = "نهایی شده"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT,
                             related_name="user_cart_list")
    create_date = models.DateTimeField(default=timezone.now, blank=False, null=False, verbose_name="Create Date")
    payment_data = models.DateField(blank=True, null=True, verbose_name="Payment Date")
    status = models.CharField(max_length=10, choices=CartStatus.choices, default=CartStatus.CART,
                              validators=[validators.MinLengthValidator(3)], blank=False, null=False)
    total_price = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="Total Price")

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"Cart #{self.pk}"


class ExclusiveStatus(models.TextChoices):
    NEW = "جدید"
    RESPONSE = "در انتظار پاسخ"
    ORDER = "در انتظار تایید کاربر"
    SUBMIT = "سفارش داده شده"
    CLOSED = "بسته شده"


class ExclusiveOrder(models.Model):
    customer = models.ForeignKey(User, on_delete=models.PROTECT, blank=False, null=False,
                                 related_name='exclusive_order_request')
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True,
                                 related_name='exclusive_order_response')
    title = models.CharField(max_length=73, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    description = models.TextField(max_length=300, blank=False, null=False)
    request_date = models.DateTimeField(default=timezone.now, blank=False, null=False, verbose_name="Request Date")
    status = models.CharField(max_length=23, choices=ExclusiveStatus.choices, default=ExclusiveStatus.NEW)
    content = models.JSONField(default=dict, blank=False, null=False)
