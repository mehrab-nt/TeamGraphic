from django import forms
from .models import UserTG
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email')


class UserTGForm(forms.ModelForm):
    class Meta:
        model = UserTG
        fields = ('profile', 'introduction')
