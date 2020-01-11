from django.shortcuts import render
from .models import User, UserTG
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from interface.views import base_context


@login_required
def user_logout(request):
    logout(request)
    print('log out')
    return HttpResponseRedirect('/', request)


def user_signup(request):
    registered = False
    if request.method == 'POST':
        current = request.POST.get('current')
        username = request.POST.get("username")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        user = User.objects.create(username=username, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        user_tg = UserTG.objects.create(user=user, confirm_code='0000')
        if 'profile' in request.FILES:
            print('found it')
            user_tg.profile = request.FILES['profile']
        user_tg.save()
        registered = True
        login(request, user)
        return HttpResponseRedirect(str(current), request)
    else:
        return HttpResponseRedirect('/', request)


def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/', request)
    if request.method == 'POST':
        current = request.POST.get('current')
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                print(str(request.path))
                return HttpResponseRedirect(str(current), request)
            else:
                return HttpResponseRedirect(str(current), request)
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username, password))
            return HttpResponseRedirect(str(current), request)
    else:
        return HttpResponseRedirect('/', request)


@login_required
def user_profile(request):
    return render(request, 'user/profile.html', base_context(request))
