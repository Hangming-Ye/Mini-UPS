from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
from tmp_wyj import *
import world_ups_pb2 as W2P
import U2A_pb2 as U2A
from tmp_wyj import *

'''
@Desc   : parse the message from UPS
@Arg    : Byte UResponses message
@Return : proto object UResponses message
'''
def parseWResp(msg):
    worldResp = W2P.UResponses()
    worldResp.ParseFromString(msg)
    return worldResp

'''
@Desc   :handle each command in the worldResp
@Arg    :
@Return :
'''
def handlewResp(worldResp, fdW, fdA):
    for completion in worldResp.completions:
        handleUFinished(completion, fdW, fdA)
        
    for delivery in worldResp.delivered:
        handleUDeliveryMade(delivery, fdW, fdA)

    for ack in worldResp.acks:
        handleAck(ack, fdW, fdA)

    for truck in worldResp.truckstatus:
        handleTruck(truck, fdW, fdA)

    for err in worldResp.error:
        print(err)

    if worldResp.HasField("finished") and worldResp.finished:  # close connection
        print("disconnect successfully")

def handleUFinished(completion, fdW, fdA):
    print(completion)

def handleUDeliveryMade(delivery, fdW, fdA):
    print(delivery)

def handleAck(ack, fdW, fdA):
    print(ack)

def handleTruck(truck, fdW, fdA):
    print(truck)


'''
@Desc   :Connect to the world
@Arg    :world_socket, Truck Number
@Return :worldid
'''
def myConnectWorld(world_socket, truck_num):
    uconnect = world_ups_pb2.UConnect()
    uconnect.isAmazon = False
    for i in range(truck_num):
        truck_to_add = uconnect.trucks.add()
        truck_to_add.id = i + 1
        x = 0
        y = 0
        truck_to_add.x = x
        truck_to_add.y = y
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

if __name__ == "__main__":
    fdW = connectServer()
    wid = connectWorld(fdW, 10)
    ucommand = world_ups_pb2.UCommands()
    pickupReq = ucommand.pickups.add()
    pickupReq.truckid = 1
    pickupReq.whid = 1
    pickupReq.seqnum = 2
    send_msg(fdW, ucommand)
    msg = recv_msg(fdW)
    resp = parseWResp(msg)
    handlewResp(resp, fdW, None)
