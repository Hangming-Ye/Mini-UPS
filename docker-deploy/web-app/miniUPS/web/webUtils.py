#1. 给user_id，或者 name，返回package list
#2. 建个地址表（地址id, location_x,y, 地址名字，owner_id(外键)）
#3. 给一个user_id，拿到所有的地址
from .models import *
def getPackagesByUser(uid):
    packages = Package.objects.filter(pk=uid)
    package_list = [package.dto() for package in packages]
    context = {'packageList': package_list}
    return context

def getLoc(user_id):
    locs = Address.objects.filter(owner_id = user_id)
    addr_list = [loc.dto() for loc in locs]
    context = {'addr_list': addr_list}
    return context
 


