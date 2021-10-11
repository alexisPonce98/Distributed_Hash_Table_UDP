from os import read
import socket, json, threading, sys, csv

processName:str
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverIP:int
serverSocket:int
amountInDHT = 0
inDHTTable = {}
leftIP = 0
rightIP = 0
leftSock = 0
rightSock = 0
myID = 0
listening = False
sending = False
portL = 0
portR = 0
#register long_name IP port(s)
def register(parsedList):
    global serverIP, serverSocket
    print("Registering")
    processName = parsedList[1]
    print("This is the second input: " + parsedList[1])
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
    global listening, portL, myID
    listening = True
    while True:
        listenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listenSocket.bind(('', portL))
        message, ADDR = listenSocket.recvfrom(2048)
        decodedMessage = message.decode()
        data = json.loads(decodedMessage)
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
        elif "query":
            print("Starting query")
        print("\n")
        print("Got a message")
        print(decodedMessage)
        print("My ID is: ")
        print(myID)

def setupLocalTable():
    print("setting up locat table")

def setupLeaderTable():
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
        for (key,val) in dataList:
            for (key,val) in val:
                if key == 3:
                    longNames.append(val)
        print("This is the fields")
        print(fields)
   
    

def dhtResponse():
    global inDHTTable, myID
    message, ADDR = clientSocket.recvfrom(2048)
    data = json.loads(message.decode())
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
    global serverIP, serverSocket
    sending = True
    wait = False
    while True:
        
        while wait:
            message, serverADDR = clientSocket.recvfrom(2048)
            print("Trying to print message")
            print(message)
            wait = False
        server = input("What is the server IP and port Number: ")
        parsedServerCommand = server.split( )

        serverIP = parsedServerCommand[0]
        serverSocket = int(parsedServerCommand[1])

        command = input("Enter client commands: ")
        parsed = command.split( )
        print(parsed)

        if parsed[0] == "register":
            print("Boutta go to register")
            register(command)
            wait = True
        elif parsed[0] == "deregister":
            print("de")
            deRegister(command)
        elif parsed[0] == "setup-dht":
            print("Sending dht setup message")
            amountInDHT = int(parsed[1])
            dhtSetup(command)
            #dhtSetupResponse()
            dhtResponse()
        elif parsed[0] == "dic":
            showData()
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


