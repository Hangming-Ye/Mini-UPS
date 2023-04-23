from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
from tmp_wyj import *
import world_ups_pb2 as W2P
import U2A_pb2 as U2A
from tmp_wyj import *

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
