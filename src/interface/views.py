from django.shortcuts import render
from .models import SlideShow, MainMenu
from product.models import Classification, Category


def base_context(request):
    context = {
        'req': request,
        'user': request.user,
        'classifications': Classification.objects.order_by('order'),
        'main_menu': MainMenu.objects.filter(active=True).order_by('rank'),
        'category': Category.objects.filter(main=True).order_by('order'),
    }
    return context


def home_view(request):
    context = base_context(request)
    tmp = {
        'slideshow_list': SlideShow.objects.filter(active=True),
    }
    context.update(tmp)
    return render(request, 'main/home.html', context)
# if request.POST:
#     try:
#         token = request.POST.get('csrfmiddlewaretoken')
