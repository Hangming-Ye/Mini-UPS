from django.http import HttpResponse
from django.urls import reverse
from .models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import *
from django.db.models import Q
from django.contrib import auth
from .webForm import *
from .webUtils import *
from django.contrib.auth.models import User
appname='web'
# 添加query的状态， 如果delivering需要访问后端
# changeLoc, 如果delivering需要访问后端
def index(request):
    if request.user.is_authenticated:
        return redirect("/profile/")
    else:
        return render(request, 'index.html')

def query(request):
    '''
    for package in Package.objects.all():
        print(package.dto())
    '''
    if request.method == 'POST':
        form = queryForm(request.POST)
        package_id = request.POST.get('package_id')
        package = Package.objects.filter(package_id = package_id)
        if package:
            if request.user.is_authenticated:
                path = 'profile.html'
            else:
                path = 'index.html'
            if package[0].status == "delivering":
                curLoc = sendQuery(package_id)
                content = package[0].dto()
                content['curLoc'] = curLoc
                return render(request, path, {'package': content})
            if package[0].status == "created" or package[0].status == "loaded":
                curLoc = "in warehouse"
            if package[0].status == "complete":
                curLoc = "already sent to destination"
            content = package[0].dto()
            content['curLoc'] = curLoc
            print(content)
            return render(request, path, {'package': content})
        else:
            return render(request, 'form.html', {'form': form,'error':"package doesn't exist"})
    else:
        form = queryForm()
        return render(request, 'form.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = registerForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['password'] != form.cleaned_data['retype_password']:
                return render(request, 'form.html', {'form': form,'error':"Two password doesn't match"})
            if User.objects.filter(email = form.cleaned_data['email']):
                return render(request, 'form.html', {'form': form,'error':"Email Address Already Exist"})
            user = User()
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
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username):
            user = auth.authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect("/profile/", {'user': user})
            else:
                print("auth failed")
                return render(request, 'form.html', {'form': form,'error':"password is incorrect"})
        else:
            return render(request, 'form.html', {'form': form,'error':"user not exist"})
    else:
        form = loginForm()
        return render(request, 'form.html', {'form': form})

@login_required()
def profile(request):
    if request.user.is_authenticated:
        uid = request.user.pk
        content = getPackagesByUser(uid)
        return render(request, 'profile.html', content)

@login_required
def changeProfile(request):
    if request.method == 'POST':
        form = modifyProfile(request.POST)
        password = request.POST.get('password')
        re_password = request.POST.get('re_password')
        if password == re_password:
            uid = request.user.pk
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            return redirect('/login/')
        else:
            return render(request, 'form.html', {'form': form,'error':"Passwords don't match!"})
    else:
        form = modifyProfile()
        return render(request, 'form.html', {'form': form, 'user': request.user})


def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
    return redirect('/login/')

login_required
def changeLoc(request, package_id):
    if request.method == 'POST':
        form = changeLocationForm(request.POST)
        location_x = request.POST.get('location_x')
        location_y = request.POST.get('location_y')
        package = Package.objects.filter(package_id = package_id)
        if package:
            if package[0].status == "delivering":
                sendLoc(package_id, location_x, location_y)
            else:
                package[0].location_x = location_x
                package[0].location_y = location_y
                package[0].save()
            return redirect('/detail/', {'package': package[0].dto()})
        else:
            return render(request, 'form.html', {'form': form,'error':"package doesn't exist"})
    else:
        form = changeLocationForm(request.POST)
        return render(request, 'form.html', {'form': form})
    
@login_required
def detail(request, package_id):
    package = Package.objects.filter(package_id=package_id)
    context = {'package': package[0].dto()}
    return render(request, 'detail.html', context)

def getSatisfaction(request, package_id):
    if request.method == 'POST':
        form = satisfactionForm(request.POST)
        rate = request.POST.get('rate')
        suggestion = request.POST.get('suggestion')
        tmp = Satisfaction(pack_id = package_id, rate = rate, suggestion = suggestion)
        tmp.save()
        return HttpResponse("Thanks for completing the form, we value your experience and suggestions. Have a good day!")
    else:
        pack = Package.objects.filter(package_id = package_id)
        if not pack or pack.status != "complete":
            pass
            # return HttpResponse("Invalid Link, package not exist or package not delivered")
        exist = Satisfaction.objects.filter(pack_id = package_id)
        if exist:
            return HttpResponse("You have already complete the form. Have a good day!")
        form = satisfactionForm()
        return render(request, 'form.html', {'form': form})


