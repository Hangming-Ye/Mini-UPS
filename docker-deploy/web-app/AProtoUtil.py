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
    amazonMsg = U2A.ACommand()
    amazonMsg.ParseFromString(msg)
    return amazonMsg


'''
@Desc   :handle each command in the AMsg
@Arg    :
@Return :
'''
def handleAMsg(session, AMsg, fdW):
    AMsg = parseWResp(AMsg)
    for pickup in AMsg.pickups:
        handleAPickup(session, pickup, fdW)
        
    for load in AMsg.toload:
        handleALoad(session, load, fdW)

    for loadComplete in AMsg.comp:
        handleALoadComplete(session, loadComplete, fdW)

    for err in AMsg.error:
        print(err)

'''
@Desc   :
@Arg    :
@Return :
'''
def handleAPickup(session, pickup, fdW, fdA):
    truckid = send_UGoPickup(session, fdW, pickup.hid, pickup.seqnum)
    send_UPickupRes(fdA, truckid, None)


'''
@Desc   :
@Arg    :
@Return :
'''
def handleALoad(session, load, fdW, fdA):
    for item in load.ItemInfo:
        item_id = item.item_id
        num = item.num
        name = item.name
        desc = item.desc
    pack = Package(package_id = load.package_id, status = PackageStatusEnum.loaded, location_x = load.location_x, 
                   location_y = load.location_y, truck_id = load.truckid, email = load.email, 
                   item_id = item_id, item_num = num, item_name = name, item_desc = desc)
    session.add(pack)
    session.commit()


'''
@Desc   :
@Arg    :
@Return :
'''
def handleALoadComplete(session, loadComplete, fdW, fdA):
    send_UGoDeliver(session, fdW, loadComplete.truckid, loadComplete.seqnum)


'''
@Desc   :
@Arg    :
@Return :
'''
def send_UPickupRes(amazon_socket, truckid, seq):
    ucommand = U2A_pb2.UCommand()
    pickupres = ucommand.upickupRes.add()
    pickupres.truckid = truckid
    pickupres.seqnum = seq
    send_msg(amazon_socket, ucommand)
    print("Sent UCommand UPickupRes")


'''
@Desc   :
@Arg    :
@Return :
'''
def send_UArrived(amazon_socket, truckid, seq):
    ucommand = U2A_pb2.UCommand()
    arrived = ucommand.uarrived.add()
    arrived.truckid = truckid
    arrived.seqnum = seq
    send_msg(amazon_socket, ucommand)
    print("Sent UCommand UArrived")


'''
@Desc   :
@Arg    :
@Return :
'''
def send_UDelivered(amazon_socket, packageid, seq):
    ucommand = U2A_pb2.UCommand()
    delivered = ucommand.udelivered.add()
    delivered.packageid = packageid
    delivered.seqnum = seq
    send_msg(amazon_socket, ucommand)
    print("Sent UCommand UDelivered")


'''
@Desc   :
@Arg    :
@Return :
'''
def send_UError(amazon_socket, err_code, msg, seq):
    ucommand = U2A_pb2.UCommand()
    error = ucommand.uerror.add()
    error.code = err_code
    if msg:
        error.msg = msg
    error.seqnum = seq
    send_msg(amazon_socket, ucommand)
    print("Sent UCommand UError")