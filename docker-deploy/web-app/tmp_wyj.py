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
import server
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint


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
def send_UGoPickup(world_socket, whid, seq):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    pickup = ucommands.pickups.add()
    pickup.whid = whid
    pickup.seqnum = seq

    #connect to db 
    engine = connectDB()
    session = getSession(engine)
    #fetch the first truckid with status = idle
    truck = session.query(Truck).filter_by(status=1).first()
    truckid = truck.truck_id
    pickup.truckid = truckid
    #update the status of this truck to driveWH
    truck.status = 2
    session.commit()
    session.close()

    while(True):
        #send UCommand to the world
        send_msg(world_socket, ucommands)
        print("Sent UCommand UGoPickup")
        #handling message lost
        time.sleep(4)
        print(server.ack_set)
        if seq in server.ack_set:
            print("Sent UCommand go pick up, already received by world")
            break
        print(" Sent UCommand go pick up, not received by world " + str(seq))
    
    return truckid

'''
@Desc   :Tell the world to let the truck deliver the packages
@Arg    :world_socket, truckid, seq
@Return :None
'''
def send_UGoDeliver(world_socket, truckid, seq):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    delivery = ucommands.deliveries.add()
    delivery.truckid = truckid
    delivery.seqnum = seq
     # Connect to database 
    engine = connectDB()
    session = getSession(engine)
    # Find all the packages which status are 'loaded' and truck_id is truckid, change status to 'delivering'
    packages = session.query(Package).filter_by(status=PackageStatusEnum.loaded, truck_id=truckid)
    for package in packages.all():
        package.status = 2
    session.commit()
    # Change this truck from 'arriveWH' to 'delivering'
    truck = session.query(Truck).filter_by(truck_id=truckid)
    truck.status = 4
    session.commit()

    for package in packages.all():
        delivery_location = delivery.packages.add()
        delivery_location.packageid = package.package_id
        delivery_location.x = package.location_x
        delivery_location.y = package.location_y

    session.close()
    print("Finished writing UGoDelivery of Ucommand")

    while(True):
        #send UCammand to world
        send_msg(world_socket, ucommands)
        print("Sent UCommand go delivery")
        #handling message lost
        time.sleep(4)
        if seq in ack_set:
            print("Sent UCommand go delivery, already recceived by world")
            break
        print("Sent UCommand go delivery, not recceived by world " + str(seq))

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
    while(True):
        send_msg(world_socket, ucommands)
        print("Sent UCommand UQuery")
        time.sleep(4)
        if seq in ack_set:
            print("Sent UCommand query, already recceived by world")
            break
        print("Sent UCommand query, not recceived by world " + str(seq))

def send_ack(world_socket, ack):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    ucommands.acks.append(ack)
    #send UCommand to world
    send_msg(world_socket, ucommands)

def send_UPickupRes(amazon_socket, truckid, seq):
    ucommand = U2A_pb2.UCommand()
    pickupres = ucommand.upickupRes.add()
    pickupres.truckid = truckid
    pickupres.seqnum = seq
    send_msg(amazon_socket, ucommand)
    print("Sent UCommand UPickupRes")

def send_UArrived(amazon_socket, truckid, seq):
    ucommand = U2A_pb2.UCommand()
    arrived = ucommand.uarrived.add()
    arrived.truckid = truckid
    arrived.seqnum = seq
    send_msg(amazon_socket, ucommand)
    print("Sent UCommand UArrived")

def send_UDelivered(amazon_socket, packageid, seq):
    ucommand = U2A_pb2.UCommand()
    delivered = ucommand.udelivered.add()
    delivered.packageid = packageid
    delivered.seqnum = seq
    send_msg(amazon_socket, ucommand)
    print("Sent UCommand UDelivered")

def send_UError(amazon_socket, err_code, msg, seq):
    ucommand = U2A_pb2.UCommand()
    error = ucommand.uerror.add()
    error.code = err_code
    if msg:
        error.msg = msg
    error.seqnum = seq
    send_msg(amazon_socket, ucommand)
    print("Sent UCommand UError")

def send_email(session, packageid):
    package = session.query(Package).filter_by(package_id = packageid).first()
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    from_email = 'sender@gmail.com'
    passw = '123'
    to_email = str(package.email)
    
    context = "Dear constomer:\n\nYour package " + str(packageid) + " has arrived, please check it!\n"\
                    + "If you have any question, please do not hesitate to contact us. Enjoy your day!\n\nUPS service center"

    message = MIMEText(context, 'plain','utf-8')
    message['Subject'] = 'UPS Delivered Confirmation' 
    message['From'] = from_email    
    message['To'] = to_email  

    try:
        email_server = smtplib.SMTP(smtp_server, smtp_port) 
        email_server.starttls()
        email_server.login(from_email, passw) 
        email_server.sendmail(from_email,to_email,message.as_string()) 
        email_server.quit() 
        print('success')
    except smtplib.SMTPException as e:
        print('error:',e) 
