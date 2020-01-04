from django import forms
from .models import Customer
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email')


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('confirm_code', 'profile')

