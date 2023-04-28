import threading
from sqlalchemy.orm import scoped_session, sessionmaker
from concurrent.futures import ThreadPoolExecutor
from db import *
from orm import *
from AProtoUtil import *
from UProtoUtil import *
from queue import Queue
import threading

WORLD_PORT = 12345
AMZ_PORT = 11111
UPS_PORT = 22222
CLIENT_PORT = 33333
AMZ_ADDR = "vcm-30971.vm.duke.edu"
TruckNum = 100
threadPool = ThreadPoolExecutor(40)
seq = 0
ack_set = set()
seqLock = threading.Lock()
fdWLock = threading.Lock()
ackLock = threading.Lock()
waitlist = Queue()
waitLock = threading.Lock()
client_socket = socket()

def worldProcess(world_ip, world_port):
    while True:
        msg = recv_msg(fdW)
        if msg is None:
            break
            """
            print("Empty message")
            connect_to_world_again(fdW, worldid)
            return
            """
        else:
            # print("######", msg)
            threadPool.submit(handlewResp, session_factory(), msg, fdW)

def AmazonProcess(amazon_addr, ups_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((socket.gethostname(), ups_port))
    sock.listen(100)
    print("----Start Listen from Amazon at Port", ups_port,"----")
    while True:
        fdA, addr = sock.accept()
        msg = recv_msg(fdA)
        fdA.close()
        if msg is None:
            fdA.close()
        else:
            threadPool.submit(handleAMsg, session_factory(), msg, fdW)

def clientProcess(client_ip, client_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((client_ip, client_port))
    sock.listen(100)
    print("----Start Listen from Front-end at Port", client_port,"----")

    while True:
        fdC, addr = sock.accept()
        msg = recv_msg(fdC)
        if msg is None:
            fdC.close()
        else:
            pass

def server():
    global session_factory, fdW
    engine = initDB()
    session_factory = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))

    fdW = connectToServer("0.0.0.0", WORLD_PORT)
    world_id = connectWorld(session_factory(), fdW, TruckNum, None)

    world = threading.Thread(target=worldProcess, args=('0.0.0.0', WORLD_PORT,))
    amazon = threading.Thread(target=AmazonProcess, args=(AMZ_ADDR, UPS_PORT, ))
    client = threading.Thread(target=clientProcess, args=('0.0.0.0', CLIENT_PORT, ))

    world.start()
    amazon.start()
    client.start()

    world.join()
    amazon.join()
    client.join()
    fdW.close()


if __name__ == "__main__":
    server()