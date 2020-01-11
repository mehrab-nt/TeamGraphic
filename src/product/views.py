from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from interface.views import base_context
from .models import Category


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
