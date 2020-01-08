from django.shortcuts import render
from .models import SlideShow


def home_view(request):
    context = {
        'user': request.user,
        'slideshow_list': SlideShow.objects.filter(active=True)
    }
    return render(request, 'main/home.html', context)
# if request.POST:
#     try:
#         token = request.POST.get('csrfmiddlewaretoken')
