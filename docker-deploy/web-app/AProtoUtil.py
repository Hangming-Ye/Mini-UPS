from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
from tmp_wyj import *
import world_ups_pb2 as W2P
import U2A_pb2 as U2A
from tmp_wyj import *
from db import *
from orm import *

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
def handleAMsg(session, AMsg, fdW, fdA):
    for pickup in AMsg.pickups:
        handleAPickup(session, pickup, fdW, fdA)
        
    for load in AMsg.toload:
        handleALoad(session, load, fdW, fdA)

    for loadComplete in AMsg.comp:
        handleALoadComplete(session, loadComplete, fdW, fdA)

    for err in AMsg.error:
        print(err)

def handleAPickup(session, pickup, fdW, fdA):
    pass
    
    

def handleALoad(session, load, fdW, fdA):
    for item in load.ItemInfo:
        item_id = item.item_id
        num = item.num
        name = item.name
        desc = item.desc
    pack = Package(package_id = load.package_id, status = PackageStatusEnum.loaded, location_x = load.location_x, 
                   location_y = load.location_y, truck_id = load.truckid, time = int(time.time()), email = load.email, 
                   item_id = item_id, item_num = num, item_name = name, item_desc = desc)
    session.add(pack)
    session.commit()


def handleALoadComplete(session, loadComplete, fdW, fdA):
    session.query(Truck).filter_by(Truck.truck_id == loadComplete.truckid).update({'status': TruckStatusEnum.delivering})
    session.commit()
    session.query(Package).filter_by(Package.truck_id == loadComplete.truckid).update({'status': PackageStatusEnum.delivering})
    session.commit()