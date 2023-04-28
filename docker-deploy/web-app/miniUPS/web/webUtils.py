from .models import *
from .client_pb2 import * 
import socket
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

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

def sendLoc(package_id: int, x: int, y: int):
    server_fd = connectToServer('0.0.0.0', 33333)

def sendQuery(package_id: int):
    server_fd = connectToServer('0.0.0.0', 33333)

'''
@Desc   : send the proto msg to destination socket
@Arg    : socketfd: destination, msg: proto object
@Return : void
'''
def send_msg(socketfd, msg):
    print("send", msg)
    string_msg = msg.SerializeToString()
    _EncodeVarint(socketfd.send, len(string_msg), None)
    socketfd.sendall(string_msg)

'''
@Desc   : receive msg from specific socket
@Arg    : socket: connected socket
@Return : binary message of the proto
'''
def recv_msg(socket):
    var_int_buff = []
    while True:
        try:
            buf = socket.recv(1)
            var_int_buff += buf
            msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
            if new_pos != 0:
                break
        except:
            whole_message = None
            return whole_message
    print("!message len", msg_len)
    whole_message = socket.recv(msg_len)
    msg = bytearray(whole_message)
    print(type(whole_message))
    while len(msg) != msg_len:
        print("fuck socket")
        tmp = socket.recv(msg_len-len(msg))
        msg.extend(bytearray(tmp))
    whole_message = bytes(msg)
    return whole_message

'''
@Desc   : connect to a server by specify ip and port
@Arg    : ip: address, port: port
@Return : socket
'''
def connectToServer(ip, port):
        fd = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            fd.connect((ip, port))
            print("Connection established to ", ip, "port", port)
        except Exception as e:
            print(e)
            print("Connection failed to ", ip, "port", port)
            exit(0)
        return fd