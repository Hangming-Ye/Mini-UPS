import psycopg2
import socket
import world_ups_pb2, U2A_pb2
import sys
import threading
import select
from msg import *
import smtplib
from email.mime.text import MIMEText
import time

from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

seq = 0
ack_set = set()

'''
@Desc   :Connect to server and get world_socket
@Arg    :None
@Return :world_socket
'''
def connectServer():
    world_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    world_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ip_port = ('0.0.0.0', 12345)
    try:
        world_socket.connect(ip_port)
        print("Socket Connected")
    except:
        print("Connection error")
        exit(0)
    return world_socket

'''
@Desc   :Connect to the world
@Arg    :world_socket, Truck Number
@Return :worldid
'''
def connectWorld(world_socket, truck_num):
    uconnect = world_ups_pb2.UConnect()
    uconnect.isAmazon = False
    
    #connect to db and initiate truck

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

    return worldid

'''
@Desc   :Send UGoPickup command to the world
@Arg    :world_socket, truckid, warehouseid, seqnum
@Return :None
'''
def send_UGoPickup(world_socket, truckid, whid, seq):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    pickup = ucommands.pickups.add()
    pickup.truckid = truckid
    pickup.whid = whid
    pickup.seqnum = seq

    #send UCommand to the world
    while True:
        send_msg(world_socket, ucommands.SerializeToString())
        print("Sent UCommand go pick up")
        #debug
        time.sleep(4)
        print(ack_set)
        if seq in ack_set:
            print("Sent UCommand go pick up, already received by world")
        else:
            print(" Sent UCommand go pick up, not received by world " + str(seq))


