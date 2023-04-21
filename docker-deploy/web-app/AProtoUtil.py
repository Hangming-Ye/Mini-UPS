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
def handleAMsg(AMsg, fdW, fdA):
    for pickup in AMsg.pickups:
        handleAPickup(pickup, fdW, fdA)
        
    for load in AMsg.toload:
        handleALoad(load, fdW, fdA)

    for loadComplete in AMsg.comp:
        handleALoadComplete(loadComplete, fdW, fdA)

    for err in AMsg.error:
        print(err)

def handleAPickup(pickup, fdW, fdA):
    seqNum = pickup.seqNum
    hid = pickup.hid
    

def handleALoad(load, fdW, fdA):
    print(load)

def handleALoadComplete(loadComplete, fdW, fdA):
    print(loadComplete)
