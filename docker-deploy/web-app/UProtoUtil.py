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
@Desc   :Connect to the world and initialize trucks
@Arg    :world_socket, Truck Number
@Return :worldid
'''
def connectWorld(session, world_socket, truck_num, world_id):
    uconnect = world_ups_pb2.UConnect()
    uconnect.isAmazon = False
    if not world_id:
        uconnect.worldid = world_id

    #connect to db and initiate truck
    for i in range(truck_num):
        truck_to_add = uconnect.trucks.add()
        truck_to_add.id = i + 1
        x = 0
        y = 0
        truck_to_add.x = x
        truck_to_add.y = y

        truck = Truck(truck_id=i+1, location_x = 0, location_y = 0, status = TruckStatusEnum.idle)
        session.add(truck)
        session.commit()

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

def reconnect_to_world(world_socket, world_id):
    uconnect = world_ups_pb2.UConnect()
    uconnect.isAmazon = False
    uconnect.worldid = world_id

    #send UConnect to world
    send_msg(world_socket, uconnect)
    print("Sent UConnect")

    #receive UConnected from world
    received = recv_msg(world_socket)

    uconnected = world_ups_pb2.UConnected()
    uconnected.ParseFromString(received)

    print("Received MSG: " + uconnected.result)

'''
@Desc   :Assign a truck to the warehouse and tell the world to send this truck to the wh
@Arg    :world_socket, truckid, warehouseid, seqnum
@Return :truckid
'''
def send_UGoPickup(session, world_socket, whid, seq):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    pickup = ucommands.pickups.add()
    pickup.whid = whid
    pickup.seqnum = seq

    #fetch the first truckid with status = idle
    truck = session.query(Truck).filter_by(status=TruckStatusEnum.idle).first()
    truckid = truck.truck_id
    pickup.truckid = truckid
    #update the status of this truck to driveWH
    truck.status = TruckStatusEnum.driveWH
    session.commit()

    #send UCommand to the world
    send_msg(world_socket, ucommands)
    print("Sent UCommand UGoPickup")
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

'''
@Desc   :Tell the world to let the truck deliver the packages
@Arg    :world_socket, truckid, seq
@Return :None
'''
def send_UGoDeliver(session, world_socket, truckid, seq):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    delivery = ucommands.deliveries.add()
    delivery.truckid = truckid
    delivery.seqnum = seq

    # Find all the packages which status are 'loaded' and truck_id is truckid, change status to 'delivering'
    packages = session.query(Package).filter_by(status=PackageStatusEnum.loaded, truck_id=truckid)
    for package in packages.all():
        package.status = PackageStatusEnum.delivering
        session.commit()

    # Change this truck from 'arriveWH' to 'delivering'
    truck = session.query(Truck).filter_by(truck_id=truckid).one()
    truck.status = TruckStatusEnum.delivering
    session.commit()

    for package in packages.all():
        delivery_location = delivery.packages.add()
        delivery_location.packageid = package.package_id
        delivery_location.x = package.location_x
        delivery_location.y = package.location_y

    print("Finished writing UGoDelivery of Ucommand")

    #send UCammand to world
    send_msg(world_socket, ucommands)
    print("Sent UCommand go delivery")
    #handling message lost
    """
        time.sleep(4)
        if seq in ack_set:
            print("Sent UCommand go delivery, already recceived by world")
            break
        print("Sent UCommand go delivery, not recceived by world " + str(seq))
    """

'''
@Desc   :Check where the truck is
@Arg    :world_socket, truckid, seq
@Return :None
'''
def send_UQuery(world_socket, truckid, seq):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    query = ucommands.queries.add()
    query.truckid = truckid
    query.seqnum = seq
    send_msg(world_socket, ucommands)
    print("Sent UCommand UQuery")
