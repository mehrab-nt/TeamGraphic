from copy import deepcopy
from django.db.models import ManyToManyField
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from product.models import ProductCategory

PRODUCT_INFO_MAP = {
    'OFF': 'offset_info',
    'LAR': 'large_format_info',
    'SLD': 'solid_info',
    'DIG': 'digital_info',
}

def clone_product(original_product, new_category):
    """
    Clone a Product object fully (including product info model and M2M fields),
    using the exact logic from your copy_product view.
    """
    # 1) Copy base product
    product_copy = deepcopy(original_product)
    product_copy.pk = None
    product_copy.parent_category = new_category

    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    product_copy.title = f"{original_product.title} (copy: {timestamp})"
    product_copy.save()

    # 2) Copy product ManyToMany
    for field in original_product._meta.get_fields():
        if isinstance(field, ManyToManyField) and not field.auto_created:
            values = getattr(original_product, field.name).all()
            getattr(product_copy, field.name).set(values)

    # 3) Copy related product info (offset_info, large_format_info, etc.)
    info_field = PRODUCT_INFO_MAP.get(original_product.type)
    if not info_field:
        product_copy.delete()
        return None

    try:
        original_info = getattr(original_product, info_field)
    except ObjectDoesNotExist:
        product_copy.delete()
        return None

    info_copy = deepcopy(original_info)
    info_copy.pk = None
    info_copy.product_info = product_copy
    info_copy.save()

    # 4) Copy M2M inside product-info model
    for field in original_info._meta.get_fields():
        if isinstance(field, ManyToManyField) and not field.auto_created:
            values = getattr(original_info, field.name).all()
            getattr(info_copy, field.name).set(values)

    return product_copy

def clone_category_tree(original, parent_copy=None):
    """
    Recursively clone a category tree including all subcategories AND
    all products inside each category using full product clone logic.
    """

    # --- Clone category ---
    new_cat = deepcopy(original)
    new_cat.pk = None
    new_cat.parent_category = parent_copy
    new_cat.title = f"{original.title} (copy)"
    new_cat.landing = None     # OneToOne cannot be reused
    new_cat.save()

    # --- Clone products inside this category ---
    from product.models import Product
    original_products = Product.objects.filter(parent_category=original)

    for product in original_products:
        clone_product(product, new_cat)

    # --- Recursively clone children ---
    for child in original.get_children():
        clone_category_tree(child, parent_copy=new_cat)

    return new_cat