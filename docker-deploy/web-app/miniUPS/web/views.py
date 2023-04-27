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
    '''
    for package in Package.objects.all():
        print(package.dto())
    '''
    if request.method == 'POST':
        form = queryForm(request.POST)
        package_id = request.POST.get('package_id')
        package = Package.objects.filter(package_id = package_id)
        print("!!!!", package)
        if package:
            return redirect('/index/', {'package': package[0]})
        else:
            return render(request, 'form.html', {'form': form,'error':"package doesn't exist"})
    else:
        form = queryForm()
        return render(request, 'form.html', {'form': form})

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
            return render(request, 'form.html', {'form': form,'error':"user name already exist"})
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
                return redirect('/index/', {'user': user})
            else:
                print("auth failed")
                return render(request, 'form.html', {'form': form,'error':"password is incorrect"})
        else:
            return render(request, 'form.html', {'form': form,'error':"user not exist"})
    else:
        form = loginForm()
        return render(request, 'form.html', {'form': form})

@login_required
def profile(request):
    pass


@login_required
def changeProfile(request):
    if request.method == 'POST':
        form = modifyProfile(request.POST)
        password = request.POST.get('password')
        re_password = request.POST.get('re_password')
        if password == re_password:
            return redirect('change-profile-done')
        else:
            return render(request, 'form.html', {'form': form,'error':"Passwords don't match!"})
    else:
        form = modifyProfile()
        return render(request, 'form.html', {'form': form})

def changedone(request):
    return HttpResponse("You've already changed your profile.")
    """
    return rediect('profile')
    """

def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
    return redirect('/login/')

def changeLoc(request, package_id):
    pass

"""
enter email version
another: get packlist directly after logged-in
"""
def packlist(request):
    pass

def detail(request):
    package_id = request.package_id
    package = Package.objects.filter(package_id=package_id) 
    context = {'package': package}
    return render(request, 'package_detail.html', context)


