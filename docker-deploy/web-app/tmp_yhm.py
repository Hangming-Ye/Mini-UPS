from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
from tmp_wyj import *
import world_ups_pb2 as W2P
import U2A_pb2 as U2A

def parseWResp(fd):
    msg = recv_msg(fd)
    worldResp = W2P.UResponses()
    worldResp.ParseFromString(msg)
    