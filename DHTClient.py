import enum
from json.encoder import py_encode_basestring
from os import read
import socket, json, threading, sys, csv, time
from typing import Collection

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
waiting_for_Query = False
#register long_name IP port(s)
def register(parsedList):
    global serverIP, serverSocket
    clientSocket.sendto(parsedList.encode(), (serverIP, serverSocket))


def deRegister(cmd):
    global serverIP, serverSocket
    print("Going to deregister")
    clientSocket.sendto(cmd.encode(), (serverIP, int(serverSocket)))

def showData():
    global serverIP, serverSocket
    clientSocket.sendto("dic".encode(), (serverIP, int(serverSocket)))

def dhtSetup(cmd):
    global serverIP, serverSocket
    clientSocket.sendto(cmd.encode(), (serverIP, int(serverSocket)))

def query_dht(cmd):
    print("Sending a query to the server")
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



def dhtSetupResponse():

    amountReceived = 0
    while amountReceived != amountInDHT:
        print("checking recieved messages fron setup DHT")
        message, serverADDR = clientSocket.recvfrom(2048)
        decodedMessage = message.decode()
        print(decodedMessage)
        amountReceived += 1


def sendToNeighbor(dicToSend):
    global rightIP, rightSock
    data = json.dumps({"Left" : dicToSend})
    print("Sending to ")
    print(rightIP)
    print(rightSock)
    clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))

def recieveMessage():
    print("Started listening")
    global listening, portL, myID, waiting_for_Query, amountInDHT
    print("Real amount " + str(amountInDHT))
    listening = True
    while True:
        listenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listenSocket.bind(('', portL))
        message, ADDR = listenSocket.recvfrom(2048)
        
        print("Message reccieved")
        decodedMessage = message.decode()
        #print(decodedMessage)
        data = json.loads(decodedMessage)
        #print(data)
        if "QUERY-START" in data:
            print("YUP its here")
        edge = False
        if "Left" in data:
            clientRingList = data["Left"]
            print(clientRingList)
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
                        print("at the edge of ring")
                        edge = True
                else:
                    dhtToSend[key] = val
            if edge == False:
                sendToNeighbor(dhtToSend)
        elif "DATA" in data:
            print("This is the length of the list: "+ str(len(myDHTData)))
            print("Got data from left neighbor")
            recievedData = data["DATA"]
            #print(recievedData)
            justStarted = True
            if recievedData[0] == myID:
                print("This is my data")
                LM:str
                
                for (key,val) in enumerate(recievedData[2]):
                        if key == 3:
                            LM = val
                print("This is the key being inserted " + str(LM))
                myDHTData[LM] = recievedData[2]
                print(recievedData[2])
            else:
                clientSocket.sendto(message, (str(rightIP), int(rightSock)))
        elif "START" in data:
            recievedData = data["START"]
            if recievedData[0] == 'FAILURE':
                print("Either you are in DHT/ No register with server/ DHT not setup yet")
                waiting_for_Query = False
            else:
                print("SUCCESS")
                query_long_name = input()
                parsedInput = query_long_name.split( )
                if parsedInput[0] == 'query':
                    print(parsedInput)
                    long_Name = ""
                    for (key, val) in enumerate(parsedInput):
                        print("THIS IS THE key" + str(key))
                        print("This is he len " + str(len(parsedInput)))
                        if key == len(parsedInput)-1:
                            
                            long_Name += val
                        elif key > 0:
                            long_Name += val
                            long_Name += " "
                    print("After the for " + str(long_Name))
                    data = json.dumps({"init" : [long_Name, portL]})
                    clientSocket.sendto(data.encode(), (str(recievedData[0]), int(recievedData[1])))
                else:
                    print("Wrong input, looking for <query> <long Name>")

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
            print("pos" + str(pos))
            print("Amount" + str(amountInDHT))
            id = pos % amountInDHT
            if id == myID:
                print("This is my data")
                dhtData = myDHTData[long_Name]
                print("Sending")
                print(dhtData)
                print("to " + str(ADDR[0]) + " " + str(int(return_port)))
                data = json.dumps({"result": dhtData})
                clientSocket.sendto(data.encode(), (str(ADDR[0]), int(return_port)))
            else:
                print("Not my data moving it along")
                data = json.dumps({"Look": [id, pos, long_Name, ADDR[0], return_port]})
                clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
        elif "Look" in data:
            recievedData = data["Look"]
            return_port = recievedData[4]
            return_addr = recievedData[3]
            long_Name = recievedData[2]
            if recievedData[0] == myID:
                print("This is my data")
                dhtData = myDHTData[long_Name]
                data = json.dumps({"result": dhtData})
                clientSocket.sendto(data.encode(), (str(return_addr), int(return_port)))
            else:
                print("Not my data moving it along")
                data = json.dumps({"Look": [recievedData[0], recievedData[1],long_Name, return_addr, return_port]})
                clientSocket.sendto(data.encode(), (str(rightIP), int(rightSock)))
        elif "result" in data:
            print("Got my result")
            recievedData = data["result"]
            print(recievedData)
            waiting_for_Query = False
        elif "deregister" in data:
            recievedData = data["deregister"]
            print(recievedData)
        
       # print("\n")
       # print("Got a message")
       # print(decodedMessage)
       # print("My ID is: ")
       # print(myID)

def setupLocalTable():
    print("setting up locat table")

def setupLeaderTable():
    global myName
    dataList = []
    print("Leader setting up table")
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
                    print("This is the pos")
                    print(pos)
                    print("This is the amount in dht")
                    print(amountInDHT)
                    id = pos % amountInDHT
                    if id != myID:
                        print("Going to sends data to next dht")
                        arrary_being_sent_to_neighbor = [id, pos, data_val]
                        sentJson = json.dumps({"DATA" : arrary_being_sent_to_neighbor})
                        clientSocket.sendto(sentJson.encode(), (str(rightIP), int(rightSock)))
                    else:
                        print("This is my data")
                        print("inserting key of " + str(val))
                        myDHTData[val] = data_val
                        print(data_val)
                    ascii_values.append(sum_of_word)
                    longNames.append(val)
        print("This is my dht table")
        print(myDHTData)
        print("This is my name")
        print(myName)
        dht_complete_message = "dht-complete " + str(myName)
        clientSocket.sendto(dht_complete_message.encode(), (str(serverIP), int(serverSocket)))


   
    

def dhtResponse():
    global inDHTTable, myID
    message, ADDR = clientSocket.recvfrom(2048)
    decodedMSG = message.decode()
    print(decodedMSG)
    data = json.loads(decodedMSG)
    print(data)
    print("is what i got from dht setup")
    passedDHT = data.get("Table")
    inDHTTable = passedDHT
    print(inDHTTable)
    dicTOSend = {}
    for (key,val) in inDHTTable.items():
        if key == "0":
            global rightIP
            global rightSock
            temp = list(inDHTTable)
            next = temp[temp.index(key) +1]
            rightIP = inDHTTable[next][1]
            rightSock = int(inDHTTable[next][2])
        else:
            dicTOSend[key] = val
    print("Sending: ")
    print(dicTOSend)
    sendToNeighbor(dicTOSend)
    setupLeaderTable()
    print("My ID is: ")
    print(myID)
    sendMessage()

    
def dht_complete_response():
    print("Waiting")
    waiting = True
    while waiting:
        msg, addr = clientSocket.recvfrom(2048)
        decodedMSG = msg.decode()
        if decodedMSG == "SUCCESS":
            print("SUCCESS")
        else:
            print("FAILURE")
        waiting = False
 
def sendMessage():
    global serverIP, serverSocket, amountInDHT, waiting_for_Query
    sending = True
    wait = False
    while True:
        
        while wait:
            message, serverADDR = clientSocket.recvfrom(2048)
            print("Trying to print message")
            print(message)
            wait = False
        
        while waiting_for_Query:
            time.sleep(1)

        server = input("What is the server IP and port Number: ")
        parsedServerCommand = server.split( )

        serverIP = parsedServerCommand[0]
        serverSocket = int(parsedServerCommand[1])

        command = input("Enter client commands: ")
        parsed = command.split( )
        print(parsed)

        if parsed[0] == "register":
            global myName
            print("Boutta go to register")
            myName = parsed[1]
            register(command)
            wait = True
        elif parsed[0] == "deregister":
            print("de")
            deRegister(command)
        elif parsed[0] == "setup-dht":
            print("Sending dht setup message")
            amountInDHT = int(parsed[1])
            print("This is the amount in dht" +  str(amountInDHT))
            dhtSetup(command)
            #dhtSetupResponse()
            dhtResponse()
        elif parsed[0] == "dic":
            showData()
        elif parsed[0] == 'query-dht':
            command += " "
            command += str(portL)
            print(command)
            waiting_for_Query = True
            query_dht(command)
        elif parsed[0] == "send":
            clientSocket.sendto(parsed[1].encode(), (serverIP, int(serverSocket)))
        elif command == "exit":
            break
        elif parsed[0] == "dht-complete":
            clientSocket.sendto(command.encode(), (serverIP, int(serverSocket)))
            dht_complete_response()
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


