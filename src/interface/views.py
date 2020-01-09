from django.shortcuts import render
from .models import SlideShow, MainMenu
from product.models import Classification


def home_view(request):
    context = {
        'user': request.user,
        'slideshow_list': SlideShow.objects.filter(active=True),
        'classifications': Classification.objects.order_by('order'),
        'main_menu': MainMenu.objects.filter(active=True).order_by('rank')
    }
    return render(request, 'main/home.html', context)
# if request.POST:
#     try:
#         token = request.POST.get('csrfmiddlewaretoken')
