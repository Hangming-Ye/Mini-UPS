from .models import *
from .client_pb2 import * 
import socket
from .sockUtil import *

def getPackagesByUser(uid):
    email = User.objects.filter(pk=uid)[0].email
    packages = Package.objects.filter(email = email)
    package_list = [package.dto() for package in packages]
    context = {'packageList': package_list}
    return context

def getLoc(user_id):
    locs = Address.objects.filter(owner_id = user_id)
    addr_list = [loc.dto() for loc in locs]
    context = {'addr_list': addr_list}
    return context

def sendLoc(package_id: int, x: int, y: int):
    server_fd = connectToServer('0.0.0.0', 33333)
    ccommand = CCommand()
    newLoc = ccommand.newLoc.add()
    newLoc.packageid = package_id
    newLoc.location_x = x
    newLoc.location_y = y
    send_msg(server_fd, ccommand)
    return recvLoc(server_fd)

def sendQuery(package_id: int):
    server_fd = connectToServer('0.0.0.0', 33333)
    ccommand = CCommand()
    query = ccommand.query.add()
    query.packageid = package_id
    send_msg(server_fd, ccommand)
    return recvQuery(server_fd)
    
def recvQuery(fd):
    return "Currently deliverying at location (x,y)"

def recvLoc(fd):
    return True