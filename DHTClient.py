from ast import parse
import enum
from json.encoder import py_encode_basestring
from os import read
import socket, json, threading, sys, csv, time
from typing import Collection
import os

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverIP:int
serverSocket:int
amountInDHT = 0
inDHTTable = {}
#myDHTData = list(range(0, 352))
myDHTData = {}
leftIP = 0
rightIP = 0
leftSock = 0
rightSock = 0
myID = 0
listening = False
sending = False
portL = 0
portR = 0
myName:str
myIP:str
mySock:int
waiting_for_Query = False
started__teardown = False
leader = False
leave_user:str
am_leader = False
#register long_name IP port(s)
def register(parsedList):
    global serverIP, serverSocket
    clientSocket.sendto(parsedList.encode(), (serverIP, serverSocket))


def deRegister(cmd):
    global serverIP, serverSocket
   #("Going to deregister")
    clientSocket.sendto(cmd.encode(), (serverIP, int(serverSocket)))

def showData():
    global serverIP, serverSocket
    clientSocket.sendto("dic".encode(), (serverIP, int(serverSocket)))

def dhtSetup(cmd):
    global serverIP, serverSocket
    clientSocket.sendto(cmd.encode(), (serverIP, int(serverSocket)))

def query_dht(cmd):
    #print("Sending a query to the server")
    global serverIP, serverSocket
    
    clientSocket.sendto(cmd.encode(), (str(serverIP), int(serverSocket)))
    #wait_for_query_response()

# might not need this wait function
def wait_for_query_response():
    msg, addr = clientSocket.recvfrom(2048)
    decodedMSG = msg.decode()
    data = json.loads(decodedMSG)
    if 'FAILURE' in data:
        print("FAILURE")
    elif 'SUCCESS' in data:
        query_input = input("SUCCESS: What data are you looking for?")

def join_dht(cmd):
    global serverSocket, serverIP
    clientSocket.sendto(cmd.encode(), (str(serverIP), int(serverSocket)))

def dhtSetupResponse():

    amountReceived = 0
    while amountReceived != amountInDHT:
       # print("checking recieved messages fron setup DHT")
        message, serverADDR = clientSocket.recvfrom(2048)
        decodedMessage = message.decode()
        #print(decodedMessage)
        amountReceived += 1


def sendToNeighbor(dicToSend, leader_ip, leader_sock):
    global rightIP, rightSock
    data = json.dumps({"Left" : [dicToSend, leader_ip, leader_sock]})
    #print("Sending to ")
   # print(rightIP)
   # print(rightSock)
    clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))

def recieveMessage():
    #print("Started listening")
    global listening, portL, myID, waiting_for_Query, amountInDHT, myDHTData, leader, leave_user, am_leader
    #print("Real amount " + str(amountInDHT))
    listening = True
    while True:
        listenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listenSocket.bind(('', portL))
        message, ADDR = listenSocket.recvfrom(2048)
        
       # print("Message reccieved")
        decodedMessage = message.decode()
        #print(decodedMessage)
        data = json.loads(decodedMessage)
        #print(data)
        edge = False
        if "Left" in data:
            real_data = data["Left"]
            leader_ip = real_data[1]
            leader_sock = real_data[2]
            clientRingList = real_data[0]
            #print(clientRingList)
            justStarted = True
            dhtToSend = {}
            for (key,val) in clientRingList.items():
                if justStarted:
                    global myID, rightSock, rightIP
                    myID = int(key)
                    temp = list(clientRingList)
                    try:
                        index = temp[temp.index(key) + 1]
                        if index in clientRingList:
                            next = temp[temp.index(key) +1]
                            rightIP = clientRingList[next][1]
                            rightSock = clientRingList[next][2]
                        justStarted = False
                    except:
                        rightIP = leader_ip
                        rightSock = leader_sock
                        #print("at the edge of ring")
                        edge = True
                else:
                    dhtToSend[key] = val
            if edge == False:
                sendToNeighbor(dhtToSend, leader_ip, leader_sock)
        elif "DATA" in data:
           # print("Got data from left neighbor")
            recievedData = data["DATA"]
            #print(recievedData)
            justStarted = True
            if recievedData[0] == myID:
               # print("This is my data")
                LM:str
                
                for (key,val) in enumerate(recievedData[2]):
                        if key == 3:
                            LM = val
               # print("This is the key being inserted " + str(LM))
                myDHTData[LM] = recievedData[2]
                print(recievedData[2])
            else:
                clientSocket.sendto(message, (str(rightIP), int(rightSock)))
        elif "START" in data:
            recievedData = data["START"]
            if recievedData[0] == 'FAILURE':
               # print("Either you are in DHT/ No register with server/ DHT not setup yet")
                waiting_for_Query = False
            else:
                print("SUCCESS")
                query_long_name = input()
                parsedInput = query_long_name.split( )
                if parsedInput[0] == 'query':
                   # print(parsedInput)
                    long_Name = ""
                    for (key, val) in enumerate(parsedInput):
                       # print("THIS IS THE key" + str(key))
                       # print("This is he len " + str(len(parsedInput)))
                        if key == len(parsedInput)-1:
                            
                            long_Name += val
                        elif key > 0:
                            long_Name += val
                            long_Name += " "
                    #print("After the for " + str(long_Name))
                    data = json.dumps({"init" : [long_Name, portL]})
                    clientSocket.sendto(data.encode(), (str(recievedData[0]), int(recievedData[1])))

        elif "QUERY-leader" in data:
            # recieved a connection confirmation from the leader
            print("What data would you like to qeury? ")
            recievedData = data["QUERY-leader"]
            query_port = recievedData[0]
            query_IP = ADDR[0]
            query_input = input("SUCESS: what data are you looking for?")
            data = json.dumps({"QUERY-init": [query_input, portL]})
            clientSocket.sendto(data.encode(), (str(query_IP), int(query_port)))
        elif "init" in data:
            # begining to look for the data
            print("checking if i have the data")
            recievedData = data["init"]
            long_Name = recievedData[0]
            return_port = recievedData[1]
            sum = 0
            for letter in long_Name:
                sum += ord(letter)
            pos = sum % 353
           # print("pos" + str(pos))
           # print("Amount" + str(amountInDHT))
            id = pos % amountInDHT
            if id == myID:
                print("This is my data")
                dhtData = myDHTData[long_Name]
               # print("Sending")
               # print(dhtData)
               # print("to " + str(ADDR[0]) + " " + str(int(return_port)))
                data = json.dumps({"result": dhtData})
                clientSocket.sendto(data.encode(), (str(ADDR[0]), int(return_port)))
            else:
               # print("Not my data moving it along")
                data = json.dumps({"Look": [id, pos, long_Name, ADDR[0], return_port]})
                clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
        elif "Look" in data:
            recievedData = data["Look"]
            return_port = recievedData[4]
            return_addr = recievedData[3]
            long_Name = recievedData[2]
            if recievedData[0] == myID:
                print("This is my data")
               # print(recievedData[0])
               # print(myID)
                dhtData = myDHTData[long_Name]
                data = json.dumps({"result": dhtData})
                clientSocket.sendto(data.encode(), (str(return_addr), int(return_port)))
            else:
                print("Not my data moving it along")
                data = json.dumps({"Look": [recievedData[0], recievedData[1],long_Name, return_addr, return_port]})
                clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
        elif "result" in data:
           # print("Got my result")
            recievedData = data["result"]
            print(recievedData)
            waiting_for_Query = False
        elif "deregister" in data:
            recievedData = data["deregister"]
            if recievedData == 'SUCCESS':
                print("SUCCESS")
                os._exit(1)
            else:
                print("FAILURE")
            #print(recievedData)
        elif "leave" in data:
            recievedData = data["leave"]
            if recievedData[0] == 'SUCCESS':
                print("SUCCESS")
                right_neighbor = recievedData[1]
              #  print(right_neighbor)
                teardown()
            elif recievedData[0] == "FAILURE":
                print("FAILURE")
        elif "teardown" in data:
           # print("recieved teardown")
            recievedData = data["teardown"]
            if recievedData[0] == 'yes':
                print("deleting my dht info")
                leave_user = recievedData[1]
                myDHTData = {}
                data = json.dumps({"teardown" : ['no', myName]})
                clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
            else:
                if started__teardown:
                   # print("Got back the teardown instruction")
                    myDHTData = {}
                    reset_id()
                else:
                   # print("deleting my dht info")
                    myDHTData = {}
                    data = json.dumps({"teardown": ["no", myName]})
                    clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
        elif "reset" in data:
           # print("recieved id reset command")
            recievedData = data["reset"]
            if recievedData[1] == "leader":
                myID = recievedData[0]
                amountInDHT = recievedData[2]
                data = json.dumps({"reset" : [myID, "not", amountInDHT]})
                clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock))) 
            else:
                if not leader:
                    #print("recieved id " + str(recievedData[0]))
                    myID = recievedData[0] + 1
                    amountInDHT = recievedData[2]
                    data = json.dumps({"reset" : [myID, "not", amountInDHT]})
                    clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
                else:
                    reset_ring()
        elif "new_ring" in data:
           # print("Reseting the ring")
            recievedData = data["new_ring"]
            #print("comparing " + str(recievedData[2]) + " with " + str(rightSock))
            if int(recievedData[2]) == int(rightSock):
                print("need to reset my port")
                oldSock = rightSock
                oldIP = rightIP
                rightSock = recievedData[0]
                rightIP = recievedData[1]
               # print("my new neighbor is " + str(portL))
                data = json.dumps({"right" : "done"})
                clientSocket.sendto(data.encode(), (str(oldIP), int(oldSock)))
            else:
               # print("no negihbor does")
                data = json.dumps({"new_ring" : recievedData})
                clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
        elif "right" in data:
           # print("done reseting the ring")
            data = json.dumps({"rebuild" : "please"})
            clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
        elif "rebuild" in data:
           # print("rebuilding the dht")
            rebuild_dht()
        elif "rebuilt" in data:
            recievedData = data['rebuilt']
            if recievedData == "SUCCESS":
                print("SUCCESS")
            else:
                print("FAILRE")
        elif "join" in data:
            recievedData = data["join"]
           # print("got join message")
            #data = json.dumps({'request' : [portL, myIP, recievedData[1]]})
            data = json.dumps({"break" : ["yes", myName, myIP, mySock]})
            clientSocket.sendto(data.encode(), (str(recievedData[0]), int(recievedData[1])))
        elif 'break' in data:
            recievedData = data['break']
            if recievedData[0] == 'yes':
              #  print("leader resetting dht")
                myDHTData = {}
                new_name = recievedData[1]
                new_ip = recievedData[2]
                new_sock = recievedData[3]
                amountInDHT = amountInDHT + 1
                data = json.dumps({'break' : ['no', new_name, new_ip, new_sock, mySock, amountInDHT]})
                clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
            else:
                
               # print("non leader deleting dht " + recievedData[4])
                myDHTData = {}
                if rightSock == recievedData[4]:
                    print("at the edge")
                    new_name = recievedData[1]
                    new_ip = recievedData[2]
                    new_sock = recievedData[3]
                    leader_sock = recievedData[4]
                    new_amount = recievedData[5]
                    data = json.dumps({'list' : ['yes', new_name, new_ip, new_sock, leader_sock, new_amount]})
                    clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
                else:
                    data = json.dumps({'break' : ['no', recievedData[1], recievedData[2], recievedData[3], recievedData[4], recievedData[5]]})
                    clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
        elif 'list' in data:
           # print("got list")
            recievedData = data['list']
            if recievedData[0] == 'yes':
                print(recievedData[1])
                if recievedData[4] == rightSock:
                   # print("im at the edge connecting new node")
                    oldIP = rightIP
                    oldSock = rightSock
                    new_sock = recievedData[3]
                    new_ip = recievedData[2]
                    rightIP = new_ip
                    rightSock = new_sock
                    new_amount = recievedData[5]
                    amountInDHT = new_amount
                    data = json.dumps({'list' : ['no', oldSock, oldIP, recievedData[2], recievedData[3], recievedData[4], amountInDHT, myID]})
                    print(recievedData[3])
                    print(recievedData[4])
                    clientSocket.sendto(data.encode(), (str(recievedData[2]), int(recievedData[3])))
                else:
                   # print("Not at the edge trying to connect new node")
                    amountInDHT = amountInDHT + 1
                    new_name = recievedData[1]
                    new_ip = recievedData[2]
                    new_sock = recievedData[3]
                    leader_sock = recievedData[4]
                    new_amount = recievedData[5]
                    amountInDHT = new_amount
                    data = json.dumps({'list' : ['yes', new_name, new_ip, new_sock, leader_sock, new_amount]})
                    clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
            else:
               # print("New node being connected")
                rightSock = recievedData[1]
                rightIP = recievedData[2]
                amountInDHT = recievedData[6]
                myID = recievedData[7] + 1
               # print("Set ip/sock to " + str(recievedData[1]) + " " + str(recievedData[2]))
                data = json.dumps({"recalculate" : amountInDHT})
                clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
        elif 'recalculate' in data:
           # print("trying to recalculate nwe dht")
            recievedData = data['recalculate']
            amountInDHT = recievedData
            recalculate_data(recievedData)
        elif "request" in data:
            recievedData = data['request']
            if int(recievedData[2]) == rightSock:
                oldIP = rightIP
                oldSock = rightSock
                rightIP = recievedData[1]
                rightSock = recievedData[0]
        elif 'destroy' in data:
            recievedData = data['destroy']
            if recievedData == 'SUCCESS':
                #print("Ready to fully destroy")
                am_leader = True
                data = json.dumps({'finish' : 'now'})
                clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
            else:
                print("FAULURE")
        elif 'finish' in data:
            recievedData = data['finish']
            if am_leader:
               # print("finished tearing down")
                myDHTData = {}
                myID = 0
                msg = 'teardown-complete ' + str(myName)
                clientSocket.sendto(msg.encode(), (str(serverIP), int(serverSocket)))
            else:
                myID = 0
                myDHTData = {}
                data = json.dumps({'finish' : 'now'})
                clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
        elif 'accomplished':
            recievedData = data['accomplished']



        
       # print("\n")
       # print("Got a message")
       # print(decodedMessage)
       # print("My ID is: ")
       # print(myID)


def leave_dht(command):
    #
    # print("Getting things set up to leave the dht")
    clientSocket.sendto(command.encode(), (str(serverIP), int(serverSocket)))

def teardown():
    global started__teardown
    global started_teardown
    #print("Starting the teardown")
    data = json.dumps({"teardown" : ["yes", myName]})
    started__teardown = True
    clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
    
def reset_id():
    #print("resetting ID")
    newAmount = amountInDHT - 1
    data = json.dumps({"reset": [0, "leader", newAmount]})
    clientSocket.sendto(data.encode(), (str(rightIP),int(rightSock)))

def reset_ring():
    #print("reseting the ring")
    data = json.dumps({"new_ring" : [rightSock, rightIP, portL]})
    clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))

def recalculate_data(amount):
    #print("recaulating")
    dataList = []
    with open("StatsCountry.csv", encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        fields = next(reader)
        for row in reader:
            dataList.append(row)
        long_names = []
        ascii_values = []
        for (key, val) in enumerate(dataList):
            data_val = val
            for (key,val) in enumerate(val):
                if key ==3:
                    sum_of_word = 0
                    for letter in val:
                        sum_of_word += ord(letter)
                    pos = sum_of_word % 353
                    id = pos % amountInDHT
                    if id != myID:
                        array_being_sent_to_beighbor = [id,pos,data_val,myIP, portL]
                        data = json.dumps({"DATA" : array_being_sent_to_beighbor})
                        clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
                    else:
                        myDHTData[val] = data_val
def rebuild_dht():
   # print("started")
    dataList = []
    with open("StatsCountry.csv", encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        fields = next(reader)
        for row in reader:
            dataList.append(row)
        longNames = []
        ascii_values = []
        for (key,val) in enumerate(dataList):
            data_val = val
            for (key,val) in enumerate(val):
                if key == 3:
                    sum_of_word = 0
                    for letter in val:
                        sum_of_word += ord(letter)
                    pos = sum_of_word % 353
                    id  = pos % amountInDHT
                    if id != myID:
                        array_being_sent_to_neighbor = [id, pos, data_val, myIP, portL]
                        data = json.dumps(({"DATA" : array_being_sent_to_neighbor}))
                        clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
                    else:
                        myDHTData[val] = data_val
        msg = "dht-rebuilt " + leave_user + " " + myName
        clientSocket.sendto(msg.encode(), (str(serverIP), int(serverSocket)))



def setupLeaderTable(leader_ip, leader_sock):
    global myName
    dataList = []
   # print("Leader setting up table")
    file = open("StatsCountry.csv")
    csvReader = csv.reader(file)
    with open("StatsCountry.csv", encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        fields = next(reader)
        for row in reader:
            dataList.append(row)
        longNames = []
        ascii_values = []
        for (key,val) in enumerate(dataList):
            data_val = val
            for (key,val) in enumerate(val):
                if key == 3:
                    sum_of_word = 0
                    for letter in val:
                        sum_of_word += ord(letter)
                    pos = sum_of_word % 353
                   # print("This is the pos")
                    print(pos)
                   # print("This is the amount in dht")
                    print(amountInDHT)
                    id = pos % amountInDHT
                    if id != myID:
                       # print("Going to sends data to next dht")
                        arrary_being_sent_to_neighbor = [id, pos, data_val, leader_ip, leader_sock]
                        sentJson = json.dumps({"DATA" : arrary_being_sent_to_neighbor})
                        clientSocket.sendto(sentJson.encode(), (str(rightIP), int(rightSock)))
                    else:
                       # print("This is my data")
                       # print("inserting key of " + str(val))
                        myDHTData[val] = data_val
                        print(data_val)
                    ascii_values.append(sum_of_word)
                    longNames.append(val)
       # print("This is my dht table")
       # print(myDHTData)
       # print("This is my name")
       # print(myName)
        dht_complete_message = "dht-complete " + str(myName)
        clientSocket.sendto(dht_complete_message.encode(), (str(serverIP), int(serverSocket)))


   
    

def dhtResponse():
    global inDHTTable, myID, leader
    message, ADDR = clientSocket.recvfrom(2048)
    decodedMSG = message.decode()
   # print(decodedMSG)
    data = json.loads(decodedMSG)
   # print(data)
   # print("is what i got from dht setup")
    passedDHT = data.get("Table")
    inDHTTable = passedDHT
    print(inDHTTable)
    dicTOSend = {}
    leader_ip:str
    leader_sock:int
    for (key,val) in inDHTTable.items():
        if key == "0":
            global rightIP
            global rightSock
            leader_ip = inDHTTable[key][1]
            leader_sock = inDHTTable[key][2]
            temp = list(inDHTTable)
            next = temp[temp.index(key) +1]
            rightIP = inDHTTable[next][1]
            rightSock = int(inDHTTable[next][2])
            leader = True
        else:
            dicTOSend[key] = val
   # print("Sending: ")
   # print(dicTOSend)
    sendToNeighbor(dicTOSend, leader_ip, leader_sock)
    setupLeaderTable(leader_ip, leader_sock)
    print("My ID is: ")
   # print(myID)
    sendMessage()

    
def dht_complete_response():
   # print("Waiting")
    waiting = True
    while waiting:
        msg, addr = clientSocket.recvfrom(2048)
        decodedMSG = msg.decode()
        if decodedMSG == "SUCCESS":
            print("SUCCESS")
        else:
            print("FAILURE")
        waiting = False


def teardown_dht(cmd):
    global serverSocket, serverIP
   # print("going to teardown")
    clientSocket.sendto(cmd.encode(), (str(serverIP), int(serverSocket)))
 
def sendMessage():
    global serverIP, serverSocket, amountInDHT, waiting_for_Query, myIP, mySock
    sending = True
    wait = False
    while True:
        
        while wait:
            message, serverADDR = clientSocket.recvfrom(2048)
          #  print("Trying to print message")
            #print(message)
            wait = False
        
        while waiting_for_Query:
            time.sleep(1)

        server = input("What is the server IP and port Number: ")
        parsedServerCommand = server.split( )

        serverIP = parsedServerCommand[0]
        serverSocket = int(parsedServerCommand[1])

        command = input("Enter client commands: ")
        parsed = command.split( )
       # print(parsed)

        if parsed[0] == "register":
            global myName
           # print("Boutta go to register")
            myName = parsed[1]
            myIP = parsed[2]
            mySock = parsed[3]
            register(command)
            wait = True
        elif parsed[0] == "deregister":
           # print("de")
            deRegister(command)
        elif parsed[0] == "setup-dht":
           # print("Sending dht setup message")
            amountInDHT = int(parsed[1])
           # print("This is the amount in dht" +  str(amountInDHT))
            dhtSetup(command)
            #dhtSetupResponse()
            dhtResponse()
        elif parsed[0] == "dic":
            showData()
        elif parsed[0] == 'query-dht':
            command += " "
            command += str(portL)
           # print(command)
            waiting_for_Query = True
            query_dht(command)
        elif parsed[0] == "send":
            clientSocket.sendto(parsed[1].encode(), (serverIP, int(serverSocket)))
        elif command == "exit":
            break
        elif parsed[0] == "dht-complete":
            clientSocket.sendto(command.encode(), (serverIP, int(serverSocket)))
            dht_complete_response()
        elif parsed[0] == "leave-dht":
            leave_dht(command)
        elif parsed[0] == "print":
            print(myDHTData)
            print("My id is: " + str(myID))
            print("The amount in dht is: " + str(amountInDHT))
            print("My left neighbor is: " + str(rightSock))
            print(myName)
        elif parsed[0] == "local":
            local = socket.gethostbyname(socket.gethostname())
            print(local)
        elif parsed[0] == "join-dht":
           # print("got join dht")
            join_dht(command)
        elif parsed[0] == 'teardown-dht':
            teardown_dht(command)
        #print("Doing something")
        

firstPort = input("What is the left port: ")
portL = int(firstPort)
secondPort = input("What is the right port: ")
portR = int(portR)

if listening == False:
    receive = threading.Thread(target= recieveMessage)
    receive.start()
if sending == False:
    sends = threading.Thread(target= sendMessage)
    sends.start()


