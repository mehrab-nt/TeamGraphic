from django.shortcuts import render
from .forms import UserForm, UserTGForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required


# def index(request):
#     return render(request, 'test/index.html')


# @login_required
# def special(request):
#     return HttpResponse("You are logged in !")


@login_required
def user_logout(request):
    logout(request)
    print('log out')
    return HttpResponseRedirect('/')


def user_signup(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        user_tg_form = UserTGForm(data=request.POST)
        if user_form.is_valid() and user_tg_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            user_tg = user_tg_form.save(commit=False)
            print(user)
            user_tg.user = user
            if 'profile' in request.FILES:
                print('found it')
                user_tg.profile = request.FILES['profile']
            user_tg.save()
            registered = True
        else:
            print(user_form.errors, user_tg_form.errors)
    else:
        user_form = UserForm()
        user_tg_form = UserTGForm()
    return render(request, 'user/signup.html',
                  {
                      'user_form': user_form,
                      'user_tg_form': user_tg_form,
                      'registered': registered
                  })


def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/', request)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('/')
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username, password))
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/')


@login_required
def user_orders(request):

    return HttpResponseRedirect('/')


@login_required
def user_profile(request):

    return HttpResponseRedirect('/')
