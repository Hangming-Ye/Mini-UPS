import socket
import threading
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

sockLock = threading.Lock()
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

'''
@Desc   : send the proto msg to destination socket
@Arg    : socketfd: destination, msg: proto object
@Return : void
'''
def send_msg(socketfd, msg):
    sockLock.acquire()
    string_msg = msg.SerializeToString()
    _EncodeVarint(socketfd.send, len(string_msg), None)
    socketfd.sendall(string_msg)
    sockLock.release()
    print("send", msg)

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
        except Exception as e:
            print(e)
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