from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect, reverse


def home_view(request):
    context = {

    }
    return render(request, 'main/home.html', context)
    # if request.POST:
    #     try:
    #         token = request.POST.get('csrfmiddlewaretoken')

