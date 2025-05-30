from django.db import models
from django.core import validators
from users.models import Role, Employee
from django.contrib.auth.models import User


class DeliveryMethod(models.Model):
    title = models.CharField(max_length=100, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    category = models.ForeignKey('DeliveryCategory', on_delete=models.CASCADE, blank=False, null=False,
                                 related_name='delivery_method_list')
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name="Sort Number")
    description = models.TextField(max_length=300, blank=True, null=True)
    states = models.JSONField(default=dict, blank=True, null=True)
    cities = models.JSONField(default=dict, blank=True, null=True)
    need_tracking_code = models.BooleanField(default=False, blank=False, null=False, verbose_name="Need Tracking Code")
    is_active = models.BooleanField(default=True, blank=False, null=False, verbose_name="Is Active")
    main_price = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="Main Price")
    public_method = models.BooleanField(default=True, blank=False, null=False, verbose_name="Public Method")
    role = models.ManyToManyField(
        Role,
        through='DeliveryForRoll',
        through_fields=('delivery_method', 'role'),
    )

    class Meta:
        ordering = ['-sort_number']
        verbose_name = "Delivery Method"
        verbose_name_plural = "Delivery Methods"

    def __str__(self):
        return f"Delivery Method: {self.title}"


class DeliveryForRoll(models.Model):
    delivery_method = models.ForeignKey('DeliveryMethod', on_delete=models.PROTECT, verbose_name="Delivery Method",
                                        related_name='all_role')
    role = models.ForeignKey(Role, on_delete=models.PROTECT,
                             related_name='delivery_method_list')
    price = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        verbose_name = "Delivery For Roll"
        verbose_name_plural = "Deliveries For Rolls"

    def __str__(self):
        return f"{self.delivery_method} - For: {self.role}"


class DeliveryCategory(models.Model):
    title = models.CharField(max_length=23, unique=True, validators=[validators.MinLengthValidator(3)],
                             blank=False, null=False)
    sort_number = models.SmallIntegerField(default=0, blank=False, null=False, verbose_name="Sort Number")
    is_active = models.BooleanField(default=True, blank=False, null=False, verbose_name="Is Active")

    class Meta:
        ordering = ['-sort_number']
        verbose_name = "Delivery Category"
        verbose_name_plural = "Delivery Categories"

    def __str__(self):
        return f"Delivery Category: {self.title}"


class DeliveryStatus(models.TextChoices):
    PENDING = "در انتظار"
    REQUESTED = "درخواست"
    SUBMITTED = "ثبت شده"


class DeliveryReceipt(models.Model):
    delivery_method = models.ForeignKey('DeliveryMethod', on_delete=models.PROTECT, blank=False, null=False, verbose_name="Delivery Method",
                                        related_name='delivery_method_in_receipt')
    receiver = models.ForeignKey(User, on_delete=models.PROTECT,
                                 related_name="delivery_receipt_list")
    phone_number = models.CharField(max_length=11, validators=[validators.MinLengthValidator(11)],
                                    blank=False, null=False, verbose_name="Phone Number")
    address = models.TextField(max_length=300, blank=True, null=True)
    postal_code = models.CharField(max_length=10, validators=[validators.MinLengthValidator(10)],
                                   blank=True, null=True, verbose_name="Postal Code")
    description = models.TextField(max_length=100, blank=True, null=True)
    request_date = models.DateTimeField(blank=True, null=True, verbose_name="Request Date")
    status = models.CharField(max_length=10, choices=DeliveryStatus.choices, default=DeliveryStatus.PENDING,
                              validators=[validators.MinLengthValidator(3)], blank=False, null=False)
    delivery_employee = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Delivery Employee",
                                          related_name="delivery_submit_list")
    delivery_date = models.DateTimeField(blank=True, null=True, verbose_name="Delivery Date")
    delivery_code = models.CharField(max_length=4, validators=[validators.MinLengthValidator(4)],
                                     blank=False, null=False, verbose_name="Delivery Code")
    tracking_code = models.CharField(max_length=30, blank=True, null=True, verbose_name="Tracking Code")
    tracking_code_date = models.DateTimeField(blank=True, null=True, verbose_name="Tracking Code Date")
    price = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ['request_date']
        verbose_name = "Delivery Receipt"
        verbose_name_plural = "Delivery Receipts"

    def __str__(self):
        return f"Delivery Receipt #{self.pk} ({self.receiver})"
