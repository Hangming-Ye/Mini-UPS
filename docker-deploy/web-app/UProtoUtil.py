import world_ups_pb2, U2A_pb2
from msg import *
from db import *
from orm import *
import time
import AProtoUtil
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
import server

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

'''
@Desc   :
@Arg    :
@Return :
'''
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
def send_UGoPickup(session, world_socket, whid):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    pickup = ucommands.pickups.add()
    pickup.whid = whid
    pickup.seqnum = get_seqnum()

    #fetch the first truckid with status = idle
    truck = session.query(Truck).filter_by(status=TruckStatusEnum.idle).first()
    if not truck:
        truck = session.query(Truck).filter_by(status=TruckStatusEnum.delivering).first()
        if not truck:
            server.waitlist = whid
    truckid = truck.truck_id
    pickup.truckid = truckid

    while(True):
        #send UCommand to the world
        send_msg(world_socket, ucommands)
        print("Sent UCommand UGoPickup")
        #handling message lost
        time.sleep(1)
        print(server.ack_set)
        if pickup.seqnum in server.ack_set:
            print("Sent UCommand go pick up, already received by world")
            break
        print(" Sent UCommand go pick up, not received by world " + str(pickup.seqnum))
    
    #update the status of this truck to driveWH
    truck.status = TruckStatusEnum.driveWH
    session.commit()
    return truckid

'''
@Desc   :Tell the world to let the truck deliver the packages
@Arg    :world_socket, truckid, seq
@Return :None
'''
def send_UGoDeliver(session, world_socket, truckid):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    delivery = ucommands.deliveries.add()
    delivery.truckid = truckid
    delivery.seqnum = get_seqnum()

    # Find all the packages which status are 'loaded' and truck_id is truckid 
    packages = session.query(Package).filter_by(status=PackageStatusEnum.loaded, truck_id=truckid)

    for package in packages.all():
        delivery_location = delivery.packages.add()
        delivery_location.packageid = package.package_id
        delivery_location.x = package.location_x
        delivery_location.y = package.location_y

    print("Finished writing UGoDelivery of Ucommand")

    while(True):
        #send UCammand to world
        send_msg(world_socket, ucommands)
        print("Sent UCommand go delivery")
        #handling message lost
        time.sleep(1)
        if delivery.seqnum in server.ack_set:
            print("Sent UCommand go delivery, already recceived by world")
            break
        print("Sent UCommand go delivery, not recceived by world " + str(delivery.seqnum))

    #change packages' status to 'delivering'
    packages.update({'status': PackageStatusEnum.delivering})
    packages.commit()

    # Change this truck from 'arriveWH' to 'delivering'
    session.query(Truck).filter_by(truck_id=truckid).update({'status': TruckStatusEnum.delivering})
    session.commit()

'''
@Desc   :Check where the truck is
@Arg    :world_socket, truckid, seq
@Return :None
'''
def send_UQuery(world_socket, truckid):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    query = ucommands.queries.add()
    query.truckid = truckid
    query.seqnum = get_seqnum()
    while(True):
        send_msg(world_socket, ucommands)
        print("Sent UCommand UQuery")
        time.sleep(1)
        if query.seqnum in server.ack_set:
            print("Sent UCommand query, already recceived by world")
            break
        print("Sent UCommand query, not recceived by world " + str(query.seqnum))

def send_ack(world_socket, ack):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    ucommands.acks.append(ack)
    #send UCommand to world
    send_msg(world_socket, ucommands)

'''
@Desc   : parse the message from UPS
@Arg    : Byte UResponses message
@Return : proto object UResponses message
'''
def parseWResp(msg):
    worldResp = world_ups_pb2.UResponses()
    worldResp.ParseFromString(msg)
    return worldResp

'''
@Desc   : handle each command in the worldResp (UResponse)
@Arg    : session: db session, worldResp: response message from world
@Return : 
'''
def handlewResp(session, worldResp, fdW, fdA):
    worldResp = parseWResp(worldResp)
    for completion in worldResp.completions:
        handleUFinished(session, completion, fdW, fdA)
        
    for delivery in worldResp.delivered:
        handleUDeliveryMade(session, delivery, fdW, fdA)

    for ack in worldResp.acks:
        handleAck(ack, fdW, fdA)

    for truck in worldResp.truckstatus:
        handleTruck(session, truck, fdW, fdA)

    for err in worldResp.error:
        print(err)

    if worldResp.HasField("finished") and worldResp.finished:  # close connection
        print("disconnect successfully")


'''
@Desc   : handle the UFinished response from world, identify which stage of truck, forward to amazon if arriving wh
@Arg    : session: db session, completion: UFinished Object
@Return : 
'''
def handleUFinished(session, completion, fdW, fdA):
    truck = session.query(Truck).filter_by(Truck.truck_id==completion.truckid).first()
    if completion.status == "arrive warehouse":
        truck.status = TruckStatusEnum.arriveWH
        session.commit()
        AProtoUtil.send_UArrived(fdA, truck.truckid, server.seq)
    else:
        truck.status = TruckStatusEnum.idle
        session.commit()

'''
@Desc   : handle the UDeliveryMade response from world, change package status, forward to amazon
@Arg    : session: db session, delivery: UDeliveryMade Object
@Return :
'''
def handleUDeliveryMade(session, delivery, fdW, fdA):
    package = session.query(Package).filter_by(Package.package_id == delivery.packageid).first()
    package.status = PackageStatusEnum.complete
    session.commit()
    AProtoUtil.send_UDelivered(fdA, package.package_id, server.seq)
    

'''
@Desc   : handle the ack of world
@Arg    : ack: ack in the response 
@Return :
'''
def handleAck(ack, fdW, fdA):
    print(ack)

'''
@Desc   : unpack the info of truck from world response
@Arg    :
@Return :
'''
def handleTruck(session, truck, fdW, fdA):
    print(truck)

def get_seqnum() -> int:
    server.seqLock.acquire()
    ans = server.seq
    server.seq += 1
    server.seqLock.release()
    return ans