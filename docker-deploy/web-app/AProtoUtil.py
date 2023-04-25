from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
from tmp_wyj import *
import world_ups_pb2 as W2P
import U2A_pb2 as U2A
from tmp_wyj import *
from db import *
from orm import *
from UProtoUtil import *

'''
@Desc   : parse the message from amazon
@Arg    : Byte Acommand message
@Return : proto object Acommand message
'''
def parseAMsg(msg):
    print("received from amazon request", msg)
    amazonMsg = U2A.ACommand()
    amazonMsg.ParseFromString(msg)
    print("parsed", amazonMsg)
    return amazonMsg


'''
@Desc   :handle each command in the AMsg
@Arg    :
@Return :
'''
def handleAMsg(session, AMsg, fdW):
    AMsg = parseAMsg(AMsg)
    print("Parsed message", AMsg)
    for pickup in AMsg.pickups:
        handleAPickup(session, pickup, fdW)
        
    for load in AMsg.toload:
        handleALoad(session, load)

    for loadComplete in AMsg.comp:
        handleALoadComplete(session, loadComplete, fdW)

    for err in AMsg.error:
        print(err)

'''
@Desc   :
@Arg    :
@Return :
'''
def handleAPickup(session, pickup, fdW):
    truckid = send_UGoPickup(session, fdW, pickup.hid)


'''
@Desc   :
@Arg    :
@Return :
'''
def handleALoad(session, load):
    print("load start")
    for item in load.itemInfo:
        print("!!!!!!!!!", item)
        item_id = item.itemid
        num = item.num
        name = item.name
        desc = item.desc
        print("^^^^^", item)
    print("name", name)
    pack = Package(package_id = load.packageid, status = PackageStatusEnum.loaded, location_x = load.location_x, 
                   location_y = load.location_y, truck_id = load.truckid, email = load.email, 
                   item_id = item_id, item_num = num, item_name = name, item_desc = desc)
    print(pack.dto())
    session.add(pack)
    print("load complete")
    session.commit()


'''
@Desc   :
@Arg    :
@Return :
'''
def handleALoadComplete(session, loadComplete, fdW):
    send_UGoDeliver(session, fdW, loadComplete.truckid)


'''
@Desc   :
@Arg    :
@Return :
'''
def send_UArrived(truckid, whid):
    ucommand = U2A_pb2.UCommand()
    arrived = ucommand.uarrived.add()
    arrived.truckid = truckid
    arrived.whid = whid
    arrived.seqnum = get_seqnum()
    print(3, ucommand)
    amazon_socket = connectToServer(server.AMZ_ADDR, server.AMZ_PORT)
    send_msg(amazon_socket, ucommand)
    amazon_socket.close()
    print("Sent UCommand UArrived")


'''
@Desc   :
@Arg    :
@Return :
'''
def send_UDelivered(packageid):
    ucommand = U2A_pb2.UCommand()
    delivered = ucommand.udelivered.add()
    delivered.packageid = packageid
    delivered.seqnum = get_seqnum()
    amazon_socket = connectToServer(server.AMZ_ADDR, server.AMZ_PORT)
    send_msg(amazon_socket, ucommand)
    amazon_socket.close()
    print("Sent UCommand UDelivered")


'''
@Desc   :
@Arg    :
@Return :
'''
def send_UError(err_code, msg):
    ucommand = U2A_pb2.UCommand()
    error = ucommand.uerror.add()
    error.code = err_code
    if msg:
        error.msg = msg
    error.seqnum = get_seqnum()
    amazon_socket = connectToServer(server.AMZ_ADDR, server.AMZ_PORT)
    send_msg(amazon_socket, ucommand)
    amazon_socket.close()
    print("Sent UCommand UError")