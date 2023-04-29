import world_ups_pb2
from msg import *
from db import *
from orm import *
import time
import AProtoUtil
import CProtoUtil
import server
import smtplib
from email.mime.text import MIMEText

wSeqNumSet = set()

'''
@Desc   :Connect to the world and initialize trucks
@Arg    :world_socket, Truck Number
@Return :worldid
'''
def connectWorld(session, world_socket, truck_num, world_id):
    uconnect = world_ups_pb2.UConnect()
    uconnect.isAmazon = False
    if world_id:
        uconnect.worldid = world_id

    #connect to db and initiate truck
    for i in range(truck_num):
        truck_to_add = uconnect.trucks.add()
        truck_to_add.id = i + 1
        x = 0
        y = 0
        truck_to_add.x = x
        truck_to_add.y = y

        truck = Truck(truck_id=i+1, location_x = 0, location_y = 0, status = TruckStatusEnum.idle)
        session.add(truck)
    session.commit()

    #send UConnect to world
    server.fdWLock.acquire()
    send_msg(world_socket, uconnect)
    server.fdWLock.release()
    print("Sent UConnect")

    #receive UConnected from world
    received = recv_msg(world_socket)

    uconnected = world_ups_pb2.UConnected()
    uconnected.ParseFromString(received)
    worldid = uconnected.worldid

    print("Received MSG: " + uconnected.result)
    print("world id is " + str(worldid))

    return worldid

'''
@Desc   :
@Arg    :
@Return :
'''
def reconnect_to_world(world_socket, world_id):
    uconnect = world_ups_pb2.UConnect()
    uconnect.isAmazon = False
    uconnect.worldid = world_id

    #send UConnect to world
    server.fdWLock.acquire()
    send_msg(world_socket, uconnect)
    server.fdWLock.release()
    print("Sent UConnect")

    #receive UConnected from world
    received = recv_msg(world_socket)

    uconnected = world_ups_pb2.UConnected()
    uconnected.ParseFromString(received)

    print("Received MSG: " + uconnected.result)

'''
@Desc   :Assign a truck to the warehouse and tell the world to send this truck to the wh
@Arg    :world_socket, truckid, warehouseid, seqnum
@Return :truckid
'''
def send_UGoPickup(session, world_socket, whid):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    ucommands.simspeed = 100
    pickup = ucommands.pickups.add()
    pickup.whid = whid
    pickup.seqnum = get_seqnum()

    #fetch the first truckid with status = idle
    server.waitLock.acquire()
    truck = session.query(Truck).filter_by(status=TruckStatusEnum.idle).first()
    if truck is None:
        truck = session.query(Truck).filter_by(status=TruckStatusEnum.delivering).first()
        if truck is None:
            server.waitlist.put(whid)
            return -1
        else:
            truck.status = TruckStatusEnum.driveWH
            truck.whid = whid
            session.commit()
            print("&&&&&", truck.dto())
    else:
        truck.status = TruckStatusEnum.driveWH
        truck.whid = whid
        session.commit()
    truckid = truck.truck_id
    pickup.truckid = truckid
    server.waitLock.release()

    while(True):
        #send UCommand to the world
        server.fdWLock.acquire()
        send_msg(world_socket, ucommands)
        server.fdWLock.release()
        print("Sent UCommand UGoPickup")
        #handling message lost
        time.sleep(1)
        print(server.ack_set)
        if pickup.seqnum in server.ack_set:
            print("Sent UCommand go pick up, already received by world")
            break
        print(" Sent UCommand go pick up, not received by world " + str(pickup.seqnum))
    
    #update the status of this truck to driveWH
    return truckid

'''
@Desc   :Tell the world to let the truck deliver the packages
@Arg    :world_socket, truckid, seq
@Return :None
'''
def send_UGoDeliver(session, world_socket, truckid):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    delivery = ucommands.deliveries.add()
    print(truckid)
    delivery.truckid = truckid
    delivery.seqnum = get_seqnum()
    print("received go delivery")
    # Find all the packages which status are 'loaded' and truck_id is truckid 
    packages = session.query(Package).filter_by(status=PackageStatusEnum.loaded, truck_id=truckid)
    
    for package in packages.all():
        print(package.dto())
        delivery_location = delivery.packages.add()
        delivery_location.packageid = package.package_id
        delivery_location.x = package.location_x
        delivery_location.y = package.location_y

    print("Finished writing UGoDelivery of Ucommand")

    while(True):
        #send UCammand to world
        server.fdWLock.acquire()
        send_msg(world_socket, ucommands)
        server.fdWLock.release()
        print("Sent UCommand go delivery")
        #handling message lost
        time.sleep(1)
        if delivery.seqnum in server.ack_set:
            print("Sent UCommand go delivery, already recceived by world")
            break
        print("Sent UCommand go delivery, not recceived by world " + str(delivery.seqnum))

    #change packages' status to 'delivering'
    packages.update({'status': PackageStatusEnum.delivering})
    session.commit()

    # Change this truck from 'arriveWH' to 'delivering'
    session.query(Truck).filter_by(truck_id=truckid).update({'status': TruckStatusEnum.delivering})
    session.commit()

    if not server.waitlist.empty():
        whid = server.waitlist.get()
        print("$$$$$$$$$$$$$$$$$$$$$$$$ remove whid:", whid, "from waitlist")
        print("current wait list, ",server.waitlist.queue)
        send_UGoPickup(session, world_socket, whid)

def send_UGoDeliver_one(session, world_socket, packageid):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    delivery = ucommands.deliveries.add()
    package = session.query(Package).filter_by(package_id=packageid).one()
    truckid = package.truck_id
    print(truckid)
    delivery.truckid = truckid
    delivery.seqnum = get_seqnum()
    print(package.dto())
    delivery_location = delivery.packages.add()
    delivery_location.packageid = packageid
    delivery_location.x = package.location_x
    delivery_location.y = package.location_y

    print("Finished writing UGoDelivery of Ucommand")

    while(True):
        #send UCammand to world
        server.fdWLock.acquire()
        send_msg(world_socket, ucommands)
        server.fdWLock.release()
        print("Sent UCommand go delivery")
        #handling message lost
        time.sleep(1)
        if delivery.seqnum in server.ack_set:
            print("Sent UCommand go delivery, already recceived by world")
            break
        print("Sent UCommand go delivery, not recceived by world " + str(delivery.seqnum))


'''
@Desc   :Check where the truck is
@Arg    :world_socket, truckid, seq
@Return :None
'''
def send_UQuery(world_socket, truckid):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    query = ucommands.queries.add()
    query.truckid = truckid
    query.seqnum = get_seqnum()
    while(True):
        server.fdWLock.acquire()
        send_msg(world_socket, ucommands)
        server.fdWLock.release()
        print("Sent UCommand UQuery")
        time.sleep(1)
        if query.seqnum in server.ack_set:
            print("Sent UCommand query, already recceived by world")
            break
        print("Sent UCommand query, not recceived by world " + str(query.seqnum))

'''
@Desc   :
@Arg    :
@Return :
'''
def send_ack(ackList, world_socket):
    ucommands = world_ups_pb2.UCommands()
    ucommands.disconnect = False
    ucommands.acks.extend(ackList)
    #send UCommand to world
    server.fdWLock.acquire()
    send_msg(world_socket, ucommands)
    server.fdWLock.release()

'''
@Desc   : parse the message from UPS
@Arg    : Byte UResponses message
@Return : proto object UResponses message
'''
def parseWResp(msg):
    worldResp = world_ups_pb2.UResponses()
    worldResp.ParseFromString(msg)
    return worldResp

'''
@Desc   : handle each command in the worldResp (UResponse)
@Arg    : session: db session, worldResp: response message from world
@Return : 
'''
def sendAckBack(worldResp, fdW):
    ackList = []
    for completion in worldResp.completions:
        ackList.append(completion.seqnum)
        
    for delivery in worldResp.delivered:
        ackList.append(delivery.seqnum)

    for truck in worldResp.truckstatus:
        ackList.append(truck.seqnum)

    for err in worldResp.error:
        ackList.append(err.seqnum)

    for ack in worldResp.acks:
        handleAck(ack)

    if len(ackList) != 0:
        send_ack(ackList, fdW)

'''
@Desc   : handle each command in the worldResp (UResponse)
@Arg    : session: db session, worldResp: response message from world
@Return : 
'''
def handlewResp(session, msg, fdW):
    worldResp = parseWResp(msg)
    sendAckBack(worldResp, fdW)
    print("!!!!! WORLD RESP", worldResp)
    for completion in worldResp.completions:
        handleUFinished(session, completion)
            
    for delivery in worldResp.delivered:
        handleUDeliveryMade(session, delivery)

    for truck in worldResp.truckstatus:
        truck_new = handleTruck(truck)
        CProtoUtil.send_SMade(truck_new)

    for err in worldResp.error:
        if err.seqnum not in wSeqNumSet:
            wSeqNumSet.add(err.seqnum)
            print(err)

    if worldResp.HasField("finished") and worldResp.finished:  # close connection
        print("disconnect successfully")

'''
@Desc   : handle the UFinished response from world, identify which stage of truck, forward to amazon if arriving wh
@Arg    : session: db session, completion: UFinished Object
@Return : 
'''
def handleUFinished(session, completion):
    if completion.seqnum not in wSeqNumSet:
        wSeqNumSet.add(completion.seqnum)
        truck = session.query(Truck).filter_by(truck_id = completion.truckid).first()
        if completion.status == "ARRIVE WAREHOUSE":
            truck.status = TruckStatusEnum.arriveWH
            session.commit()
            print(1)
            print("Truck ID: ", completion.truckid)
            print(truck.whid)
            AProtoUtil.send_UArrived(completion.truckid, truck.whid)
            print(2)
        else:
            truck.status = TruckStatusEnum.idle
            session.commit()
        

'''
@Desc   : handle the UDeliveryMade response from world, change package status, forward to amazon
@Arg    : session: db session, delivery: UDeliveryMade Object
@Return :
'''
def handleUDeliveryMade(session, delivery):
    if delivery.seqnum not in wSeqNumSet:
        wSeqNumSet.add(delivery.seqnum)
        package = session.query(Package).filter_by(package_id = delivery.packageid).first()
        package.status = PackageStatusEnum.complete
        session.commit()
        AProtoUtil.send_UDelivered(package.package_id)
        #send_email(session, delivery.packageid)
    

'''
@Desc   : handle the ack of world
@Arg    : ack: ack in the response 
@Return :
'''
def handleAck(ack):
    server.ack_set.add(ack)


'''
@Desc   : unpack the info of truck from world response
@Arg    :
@Return :
'''
def handleTruck(truck):
    if truck.seqnum not in wSeqNumSet:
        wSeqNumSet.add(truck.seqnum)
        print(truck)
        return truck

def get_seqnum() -> int:
    server.seqLock.acquire()
    ans = server.seq
    server.seq += 1
    print("@@@@@@@@@@@@@@@@@", server.seq)
    server.seqLock.release()
    return ans

def send_email(session, packageid):
    package = session.query(Package).filter_by(package_id = packageid).first()
    smtp_server = 'smtp.office365.com'
    smtp_port = 587
    from_email = 'Duke_ECE568_RSS@outlook.com'
    passw = '568zuoyezhenduo'
    to_email = str(package.email)
    
    context = "Dear constomer:\n\nYour package " + str(packageid) + " has arrived, please check it through the detail link http://127.0.0.1:8000/detail/"+str(packageid)+"/!\n"\
                    + "If you have any question, please do not hesitate to contact us and give us feedback through http://127.0.0.1:8000/form/"+str(packageid)+"/. Enjoy your day!\n\nUPS service center"

    message = MIMEText(context, 'plain','utf-8')
    message['Subject'] = 'UPS Delivered Confirmation' 
    message['From'] = from_email
    message['To'] = to_email  

    try:
        email_server = smtplib.SMTP(smtp_server, smtp_port) 
        email_server.starttls()
        email_server.login(from_email, passw) 
        email_server.sendmail(from_email,to_email,message.as_string()) 
        email_server.quit() 
        print('success')
    except smtplib.SMTPException as e:
        print('error:',e)