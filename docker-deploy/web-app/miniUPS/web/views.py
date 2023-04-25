from django.http import HttpResponse
from .models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import *
from django.db.models import Q
from django.contrib import auth
from .webForm import *

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def query(request):
    pass

def register(request):
    if request.method == 'POST':
        form = registerForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['password'] != form.cleaned_data['re_password']:
                return render(request, 'form.html', {'form': form,'error':"Two password doesn't match"})
            if User.objects.filter(email = form.cleaned_data['email']):
                return render(request, 'form.html', {'form': form,'error':"Email Address Already Exist"})
            user = myUser()
            user = User.objects.create_user(username=form.cleaned_data['username'], email = form.cleaned_data['email'], 
                                            password = form.cleaned_data['password'])
            user.save()
            return redirect('/login/')
        else:
            return render(request, 'form.html', {'form': form,'error':"input is invalid"})
    else:
        form = registerForm()
        return render(request, 'form.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = loginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username):
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                return redirect('/index/', {'user', user})
            else:
                print("auth failed")
                return render(request, 'form.html', {'form': form,'error':"user not exist"})
        else:
            return render(request, 'form.html', {'form': form,'error':"password is in correct"})
    else:
        form = loginForm()
        return render(request, 'form.html', {'form': form})

@login_required
def profile(request):
    pass

def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
    return redirect('/login/')

def changeLoc(request):
    pass

def detail(request):
    pass

