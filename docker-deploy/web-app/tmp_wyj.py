import psycopg2
import socket
import world_ups_pb2, U2A_pb2
import sys
import threading
import select
from mesg import *
import smtplib
from email.mime.text import MIMEText
import time

from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

seq = 0
ack_set = set()
worldid = 0

world_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
world_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ip_port = ('0.0.0.0', 12345)
try:
    world_socket.connect(ip_port)
    print("Socket Connected")
except:
    print("error")
    exit

uconnect = world_ups_pb2.UConnect()
uconnect.isAmazon = False
#send UConnect to world
send_msg(world_socket, uconnect.SerializeToString())
print("Sent UConnect")

#receive UConnected from world
received = recv_msg(world_socket)

uconnected = world_ups_pb2.UConnected()
uconnected.ParseFromString(received)
worldid = uconnected.worldid

print("Received MSG: " + uconnected.result)
print("world id is " + str(worldid))
