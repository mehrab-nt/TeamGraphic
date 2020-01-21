from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from interface.views import base_context
from django.shortcuts import render
from .models import Cart, Order, order_id_create, cart_id_create, Status, UploadFile
from delivery.models import Delivery
from user.models import UserTG
from product.models import Product
from django.utils import timezone


@login_required
def cart_show(request):
    context = base_context(request)
    user_name = request.user
    user = UserTG.objects.get(pk=user_name.user_tg.pk)
    if request.method == 'POST':
        cart = Cart.objects.filter(user=user, progress=True)
        if cart:  # active cart existed
            cart = cart[0]
        else:  # create new Cart
            new_id = cart_id_create('98')
            cart = Cart.objects.create(
                cart_id=new_id, user=user, create_date=timezone.now(), progress=True, total_cost=1000,
                delivery=Delivery.objects.get(pk=1)
            )
            cart.save()
            print(request.POST.get('product'))
            print(request.POST.get('product_sale'))
            print(request.POST.get('product_service'))
        new_id = order_id_create('98')
        order = Order.objects.create(
            order_id=new_id, cart=cart, status=Status.objects.get(status_id='rec'),
            product=Product.objects.get(id=request.POST.get('product')),
            ready_date=timezone.now(),
            product_cost=0, design_cost=0, tot_cost=0
        )
        order.save()
        if request.POST.get("mode") == 'u':
            for all_file in request.FILES:
                uploaded_file = UploadFile.objects.create(title=all_file, user=user, order=order)
                uploaded_file.save()
                uploaded_file.file = request.FILES[all_file]
                uploaded_file.save()
        elif request.POST.get("mode") == 'r':
            cart.duration = -1
            cart.save()

            print("###")
    if request.method == 'GET':
        pass
        # tmp = {
        #     'product': product,
        #     'product_sale': product_sale,
        #     'service_list': service,
        #     'design': design,
        #     'product_cost': product_sale.sale_price() + service_cost,
        # }
        # context.update(tmp)
    return render(request, 'order/current_cart.html', context)
