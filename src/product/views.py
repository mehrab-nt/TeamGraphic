from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from interface.views import base_context
from .models import Category, Product, product_id_create
from order.models import cart_id_create
from django.utils import timezone
from django.core import serializers


def category_show(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    # try:
    #     category = Category.objects.get(id=category_id)
    # except Category.DoesNotExist:
    #     return render(request, 'product/category.html', context)
    context = base_context(request)
    tmp = {
        'category': category,
        'products': category.all_product.order_by('id'),
    }
    context.update(tmp)
    return render(request, 'product/category.html', context)


def convert_date(date):
    return date


def product_show(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = base_context(request)
    size = [product.selling_options.all()[0].size]
    if size:
        for tmp in product.selling_options.all():
            flag = 1
            for check in size:
                if tmp.size == check:
                    flag = 0
            if flag:
                size.append(tmp.size)
    ready = [product.selling_options.all()[0].ready]
    if ready:
        for tmp in product.selling_options.all():
            flag = 1
            for check in ready:
                if tmp.ready == check:
                    flag = 0
            if flag:
                ready.append(tmp.ready)
    side = [product.selling_options.all()[0].side]
    for tmp in product.selling_options.all():
        flag = 1
        for check in side:
            if tmp.side == check:
                flag = 0
        if flag:
            side.append(tmp.side)
    side_num = len(side)
    tmp = {
        'product': product,
        'selling_options': product.selling_options.all(),
        # 'selling_options': serializers.serialize('json', product.selling_options.all()),
        'size': size,
        'ready': ready,
        'services': product.product_all_service.all().filter(active=True),
        'side_num': side_num,
        'side_type': side[0],
    }
    context.update(tmp)
    return render(request, 'product/product.html', context)


@login_required
def design_level(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        context = base_context(request)
        tmp = {
            'product': product,
            'selling_options': product.selling_options.all(),
            'services': product.product_all_service.all().filter(active=True),
            'test1': request.POST.get('product_sale'),
            'test2': request.POST.getlist('product_service'),
        }
        context.update(tmp)
        return render(request, 'product/design_level.html', context)
    if request.method == 'GET':
        return product_show(request, product_id)

