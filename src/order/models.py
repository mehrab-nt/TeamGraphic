from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.core import validators
import os


class CartStatus(models.TextChoices):
    Record = 'rec', 'در حال ثبت'
    Check = 'chk', 'ثبت شده و در حال بررسی'
    Preparation = 'pre', 'آماده سازی'
    Ready = 'rdy', 'آماده تحویل'
    Delivery = 'del', 'آماده ارسال'
    Sending = 'snd', 'ارسال شد'
    Get = 'get', 'تحویل داده شد'
    Cancel = 'can', 'لغو شده'
    Remaining = 'rem', 'صورت حساب مانده'


class Cart(models.Model):
    cart_id = models.CharField(max_length=10, primary_key=True, validators=[validators.MinLengthValidator(10)])
    user = models.ForeignKey('user.UserTG', on_delete=models.CASCADE, blank=True, null=True,
                             related_name='user_carts')
    status = models.CharField(max_length=3, blank=False, choices=CartStatus.choices, default=CartStatus.Record)
    total_cost = models.PositiveIntegerField(blank=False, validators=[validators.MinValueValidator(1000),
                                                                      validators.MaxValueValidator(99999999)])
    delivery = models.ForeignKey('delivery.Delivery', on_delete=models.SET_NULL, null=True, blank=False,
                                 related_name='all_cart')
    create_date = models.DateTimeField(default=timezone.now, blank=False)
    duration = models.IntegerField(default=0, blank=False, validators=[validators.MinValueValidator(-1),
                                                                       validators.MaxValueValidator(30)])
    delivery_date = models.DateField(blank=False, default=timezone.now)
    token = models.TextField(null=True, blank=True)
    progress = models.BooleanField(default=False)
    # payment

    def __str__(self):
        return 'Cart-{0}'.format(self.cart_id)

    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبد خرید'


def cart_id_create(year):
    try:
        obj = Cart.objects.latest('cart_id')
    except Cart.DoesNotExist:
        return 'tg-{0}10000'.format(year)
    kay_year = obj.cart_id[3:-5]
    if kay_year == year:
        new_kay = 'tg-{0}{1}'.format(year, str(int(obj.cart_id[-5:])+1))
        try:
            obj = Cart.objects.get(cart_id=new_kay)
        except Cart.DoesNotExist:
            return new_kay
    else:
        new_kay = 'tg-{0}10000'.format(year)
        try:
            obj = Cart.objects.get(cart_id=new_kay)
        except Cart.DoesNotExist:
            return new_kay
    return cart_id_create(year)


class DesignFeature(models.TextChoices):
    NEW_DESIGN = 'new', 'سفارش طراحی'
    SEND_FILE = 'snd', 'ارسال فایل طرح'
    OLD_DESIGN = 'old', 'سفارش مجدد طرح قبلی'
    NONE = 'non', 'بدون طرح'


class Order(models.Model):
    order_id = models.CharField(max_length=6, primary_key=True, validators=[validators.MinLengthValidator(6)])
    cart = models.ForeignKey('Cart', on_delete=models.SET_NULL, null=True, blank=False,
                             related_name='cart_orders')
    status = models.ForeignKey('Status', on_delete=models.SET_NULL, null=True, blank=False,
                               related_name='sub_orders')
    product = models.ForeignKey('product.Product', on_delete=models.SET_NULL, null=True, blank=False,
                                related_name='product_in_orders')
    design_feature = models.CharField(max_length=3, blank=False,
                                      choices=DesignFeature.choices, default=DesignFeature.SEND_FILE)
    design = models.ForeignKey('product.Design', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='design_in_orders')
    older_order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='top_order')
    count = models.IntegerField(default=1, blank=False, validators=[validators.MinValueValidator(1),
                                                                    validators.MaxValueValidator(10)])
    description = models.TextField(max_length=777, blank=True, validators=[validators.MinLengthValidator(3)])
    duration = models.IntegerField(default=0, blank=False, validators=[validators.MinValueValidator(0),
                                                                       validators.MaxValueValidator(30)])
    ready_date = models.DateField(blank=False)
    product_cost = models.PositiveIntegerField(blank=True, validators=[validators.MinValueValidator(0),
                                                                       validators.MaxValueValidator(99999999)])
    design_cost = models.PositiveIntegerField(blank=True, validators=[validators.MinValueValidator(0),
                                                                      validators.MaxValueValidator(99999999)])
    tot_cost = models.PositiveIntegerField(blank=True, validators=[validators.MinValueValidator(0),
                                                                   validators.MaxValueValidator(99999999)])
    product_services = models.ManyToManyField('product.ProductServices', db_index=True, blank=True,
                                              related_name="in_orders", through='product.OrderProductServices')

    def __str__(self):
        return 'Order-{0}'.format(self.order_id)

    def number_of_file(self):
        if self.design_feature != 'non':
            return self.product.file_number()
        else:
            return 0

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش'


def order_id_create(year):
    try:
        obj = Order.objects.latest('order_id')
    except Order.DoesNotExist:
        return '{0}1000'.format(year)
    kay_year = obj.order_id[:2]
    if kay_year == year:
        new_kay = '{0}{1}'.format(year, str(int(obj.order_id[-4:])+1))
        try:
            obj = Order.objects.get(cart_id=new_kay)
        except Order.DoesNotExist:
            return new_kay
    else:
        new_kay = '{0}1000'.format(year)
        try:
            obj = Order.objects.get(cart_id=new_kay)
        except Order.DoesNotExist:
            return new_kay
    return order_id_create(year)


class FileName(models.TextChoices):
    FRONT = 'base1', 'front'
    BACK = 'base2', 'back'
    FRONT_FILM = 'film1', 'front_film'
    BACK_FILM = 'film2', 'back_film'
    FRONT_GOLD = 'gold1', 'front_gold'
    BACK_GOLD = 'gold2', 'back_gold'
    FRONT_FORM = 'form1', 'front_form'
    BACK_FORM = 'form2', 'back_form'


def order_upload_file_directory_path(instance, filename):
    return './order/static/file/orders/{0}_{1}_{2}/{3}_{4}_{5}.jpg'\
        .format(timezone.datetime.now().year, timezone.datetime.now().month, timezone.datetime.now().day,
                instance.user.user, instance.order.order_id, instance.title)


class UploadFile(models.Model):
    title = models.CharField(max_length=22, blank=False, choices=FileName.choices)
    user = models.ForeignKey('user.UserTG', on_delete=models.CASCADE, blank=True, null=True,
                             related_name='user_files')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, blank=True, null=True,
                              related_name='order_files')
    file = models.ImageField(upload_to=order_upload_file_directory_path, blank=False)

    class Meta:
        verbose_name = 'فایل ها'
        verbose_name_plural = 'فایل ها'


@receiver(models.signals.post_delete, sender=UploadFile)
def auto_delete_upload_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=UploadFile)
def auto_delete_upload_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False
    try:
        old_file = UploadFile.objects.get(pk=instance.pk).file
    except UploadFile.DoesNotExist:
        return False
    new_file = instance.file
    if not old_file == new_file and old_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class Type(models.TextChoices):
    Pos = 2, 'تایید'
    Neg = 0, 'لغو'
    Emp = 1, 'بررسی'


def status_vector_directory_path(instance, filename):
    return './order/static/img/status/{0}.png'.format(instance.status_id)


class Status(models.Model):
    status_id = models.CharField(max_length=3, primary_key=True, validators=[validators.MinLengthValidator(3)])
    title = models.CharField(max_length=20, blank=False, validators=[validators.MinLengthValidator(3)])
    # category
    vector = models.ImageField(upload_to=status_vector_directory_path, blank=False)
    type = models.CharField(max_length=1, choices=Type.choices, blank=False)

    def __str__(self):
        return '{0}'.format(self.title)

    class Meta:
        verbose_name = 'وضعیت های سفارش'
        verbose_name_plural = 'وضعیت های سفارش'


@receiver(models.signals.post_delete, sender=Status)
def auto_delete_status_on_delete(sender, instance, **kwargs):
    if instance.vector:
        if os.path.isfile(instance.vector.path):
            os.remove(instance.vector.path)


@receiver(models.signals.pre_save, sender=Status)
def auto_delete_status_on_change(sender, instance, **kwargs):
    if not instance.status_id:
        return False
    try:
        old_vector = Status.objects.get(pk=instance.status_id).vector
    except Status.DoesNotExist:
        return False
    new_vector = instance.vector
    if not old_vector == new_vector and old_vector:
        if os.path.isfile(old_vector.path):
            os.remove(old_vector.path)


class OrderAction(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE,
                              related_name='order_all_actions')
    user = models.ForeignKey('user.UserTG', on_delete=models.CASCADE,
                             related_name='user_actions_on_order')
    old_status = models.ForeignKey('Status', on_delete=models.SET_NULL, blank=False, null=True,
                                   related_name='on_actions_old')
    new_status = models.ForeignKey('Status', on_delete=models.SET_NULL, blank=False, null=True,
                                   related_name='on_actions_new')
    data = models.DateTimeField(default=timezone.now, blank=False)

    def __str__(self):
        return '{0} change by {1}'.format(self.order.order_id, self.user)

    class Meta:
        verbose_name = 'تغییرات سفارش'
        verbose_name_plural = 'تغییرات سفارش'


class CartAction(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE,
                             related_name='cart_all_actions')
    old_status = models.CharField(max_length=3, blank=False, choices=CartStatus.choices)
    new_status = models.CharField(max_length=3, blank=False, choices=CartStatus.choices)
    data = models.DateTimeField(default=timezone.now, blank=False)

    def __str__(self):
        return '{0} change in {1}'.format(self.cart.cart_id, self.data)

    class Meta:
        verbose_name = 'تغییرات سبد خرید'
        verbose_name_plural = 'تغییرات سبد خرید'

