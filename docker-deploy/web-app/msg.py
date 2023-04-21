import psycopg2
import socket
import world_ups_pb2, U2A_pb2
import sys
import threading
import select

from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

def send_msg(socketfd, msg):
    msg.SerializeToString()
    _EncodeVarint(socketfd.send, len(msg), None)
    socketfd.sendall(msg)

def recv_msg(socket):
    var_int_buff = []
    while True:
        try:
            buf = socket.recv(1)
            var_int_buff += buf
            msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
            print(msg_len)
            if new_pos != 0:
                break
        except:
            whole_message = None
            return whole_message
    whole_message = socket.recv(msg_len)
    return whole_message

def connectToServer(ip, port):
        fd = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            fd.connect((ip, port))
            print("Connection established to ", ip, "port", port)
        except:
            print("Connection failed to ", ip, "port", port)
            exit(0)
        return fd