import client_pb2 
from msg import *
from db import *
from orm import *
import UProtoUtil
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
import server

def parseCReq(msg):
    clientReq = client_pb2.CCommand()
    clientReq.ParseFromString(msg)
    return clientReq

def handlecReq(session, msg, world_socket, client_socket):
    clientReq = parseCReq(msg)
    print("!!!!! Client REQ", clientReq)
    for query in clientReq.query:
        handlequery(session, world_socket, query)
            
    for newLoc in clientReq.newLoc:
        handlechangeloc(session, world_socket, client_socket, newLoc)

def handlequery(session, world_socket, query):
    package = session.query(Package).filter_by(package_id=query.packageid).one()
    truckid = package.truck_id
    UProtoUtil.send_UQuery(world_socket, truckid)

def handlechangeloc(session, world_socket, client_socket, newLoc):
    send_SChanged(client_socket,newLoc.packageid)
    package = session.query(Package).filter_by(package_id=newLoc.packageid).one()
    package.location_x = newLoc.location_x
    package.location_y = newLoc.location_y
    session.commit()
    UProtoUtil.send_UGoDeliver_one(session, world_socket, newLoc.packageid)
 
def send_SMade(client_socket, truck):
    scommand = client_pb2.SCommand()
    info = scommand.info.add()
    info.location_x = truck.x
    info.location_y = truck.y
    send_msg(client_socket, scommand)

def send_SChanged(client_socket,packageid):
    scommand = client_pb2.SCommand()
    changed = scommand.changed.add()
    changed.packageid = packageid
    send_msg(client_socket, scommand)