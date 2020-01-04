from django.shortcuts import render


def home_view(request):
    context = {
        'user': request,
    }
    return render(request, 'main/home.html', context)
    # if request.POST:
    #     try:
    #         token = request.POST.get('csrfmiddlewaretoken')

