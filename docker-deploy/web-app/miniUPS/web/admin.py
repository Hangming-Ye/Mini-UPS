from django.contrib import admin
from .models import myUser, Address
# Register your models here.

admin.site.register(myUser)

admin.site.register(Address)