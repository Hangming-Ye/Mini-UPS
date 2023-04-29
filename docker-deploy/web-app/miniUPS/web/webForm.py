from django.forms import Form, ModelForm
from django import forms
from .models import *
from django.utils.translation import gettext_lazy as _

class registerForm(ModelForm):
    retype_password = forms.CharField(required=True)
    class Meta:
        model = myUser
        fields = ['username', 'email', 'password', 'retype_password']

        labels = {
            'username': _('Username'),
            'email': _('Email Address'),
            'password': _('Password'),
            'retype_password': _('Retype Password'),
        }

        help_texts = {
            'username': 'your username is what you used for login, should be unique',
            'email': 'your email is used for link your amazon account, should be unique',
        }

class loginForm(ModelForm):
    class Meta:
        model = myUser
        fields = ['username', 'password']

        labels = {
            'username': _('Username'),
            'password': _('Password'),
        }
    
class modifyProfile(ModelForm):
    re_password = forms.CharField(required=True)
    class Meta:
        model = myUser
        fields = ['password', 're_password']

        labels = {
            're_password': _('Retype Password'),
            'password': _('Password'),
        }

class queryForm(ModelForm):
    class Meta:
        model = Package
        fields = ['package_id']

        labels = {
            'package_id': _('Trucking Number'),
        }

        help_texts = {
            'package_id': 'which is also the package id',
        }

class addLocationForm(ModelForm):
    class Meta:
        model = Address
        fields = ['name','location_x', 'location_y']

class changeLocationForm(ModelForm):
    class Meta:
        model = Package
        fields = ['location_x', 'location_y']

class satisfactionForm(ModelForm):
    class Meta:
        model = Satisfaction
        fields = ['rate','suggestion']