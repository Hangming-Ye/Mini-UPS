from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
from tmp_wyj import *
import world_ups_pb2 as W2P
import U2A_pb2 as U2A
from tmp_wyj import *
from db import *
from orm import *
import multiprocessing as MP
from AProtoUtil import *
from UProtoUtil import *
import Queue

WORLD_PORT = 12345
AMZ_PORT = 11111
UPS_PORT = 22222

TruckNum = 100

def process_init(WSocketLock, worldSocket):
    global lock, fdW
    lock = WSocketLock
    fdW = worldSocket

def server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((socket.gethostname(), UPS_PORT))
    sock.listen(100)
    print("----Start Listen from Amazon at port", UPS_PORT,"----")

    fdW = connectToServer("0.0.0.0", 12345)
    world_id = connectWorld(fdW, TruckNum)

    l = MP.Lock()
    pool = MP.Pool(processes=4, initializer=process_init, initargs=(l,))
    fdList = list()

if __name__ == "__main__":
    server()