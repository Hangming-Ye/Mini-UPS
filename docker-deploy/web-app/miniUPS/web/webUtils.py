#1. 给user_id，或者 name，返回package list
#2. 建个地址表（地址id, location_x,y, 地址名字，owner_id(外键)）
#3. 给一个user_id，拿到所有的地址
from .models import *
def getPackagesByUser(email):
    packages = Package.objects.filter(email=email)
    package_list = [{'id': package.package_id, 'status': package.status, 'truck_id':package.truck_id} for package in packages]
    context = {'package_list': package_list}
    return context

def getLoc(user_id):
    locs = Address.objects.filter(owner_id = user_id)
    addr_list = [{'location_x': loc.location_x, 'location_y':loc.location_y, 'name':loc.name} for loc in locs]
    context = {'addr_list': addr_list}
    return context
 


