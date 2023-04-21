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
from db import *
from orm import *

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
    for i in range(truck_num):
        truck_to_add = uconnect.trucks.add()
        truck_to_add.id = i + 1
        x = 0
        y = 0
        truck_to_add.x = x
        truck_to_add.y = y

    #send UConnect to world
    send_msg(world_socket, uconnect)
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
@Desc   : connect to world with specific world_id
@Arg    :
@Return :
'''


'''
@Desc   :Assign a truck to the warehouse, send UGoPickup command to the world, change the status of this truck
@Arg    :world_socket, truckid, warehouseid, seqnum
@Return :truckid
'''
def send_UGoPickup(world_socket, whid, seq):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    pickup = ucommands.pickups.add()
    pickup.whid = whid
    pickup.seqnum = seq

    #connect to db 
    #fetch the first truckid with status = idle
    #update the status of this truck to arriveWH
    
    pickup.truckid = truckid

    #send UCommand to the world
    send_msg(world_socket, ucommands.SerializeToString())
    print("Sent UCommand go pick up")
    #handling message lost
    '''
        time.sleep(4)
        print(ack_set)
        if seq in ack_set:
            print("Sent UCommand go pick up, already received by world")
            break
        print(" Sent UCommand go pick up, not received by world " + str(seq))
    '''
    return truckid

def send_UGoDeliver(world_socket, truckid, seq):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    delivery = ucommands.deliveries.add()
    delivery.truckid = truckid
    delivery.seqnum = seq
     # Connect to database 
    conn = connectDB()
    cur = conn.cursor()

    # Find all the packages which status are 'loaded' and truckid is truck_id 
    cur.execute("select packageid, location_x, location_y from package where truckid='" + str(truckid) + "' and status='loaded'")
    packages = cur.fetchall()

    # Change the status of truck from 'arriveWH' to 'delivering'

    conn.commit()
    cur.close()
    conn.close()

    for package in packages:
        delivery_location = delivery.packages.add()
        delivery_location.packageid = package[0]
        delivery_location.x = package[1]
        delivery_location.y = package[2]
    
    print("Finished writing UGoDelivery of Ucommand")

    #send UCammand to world
    send_msg(world_socket, ucommands.SerializeToString())
    print("Sent UCommand go delivery")
    #handling message lost
    """
        time.sleep(4)
        if seq in ack_set:
            print("Sent UCommand go delivery, already recceived by world")
            break
        print("Sent UCommand go delivery, not recceived by world " + str(seq))
    """

def send_UQuery(world_socket, truckid, whid, seq):
    print(truckid)
