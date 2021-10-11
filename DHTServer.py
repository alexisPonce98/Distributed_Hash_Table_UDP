from os import name
import socket
import json, sys
#need to figure out this part
#port 43006
clientName:str
state:int# 0 = free, 1 = inDHT, 2 = Leader
userDict = {}
dht_setup = False
DHTLeader:str
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock = input("What is the socket: ")
serverSocket.bind(('', int(sock)))
print("Dictionary already has: ")
print(userDict)

#registers the inputted clientName/ IPV4 and Ports
def register(parsedList):
    clientName = parsedList[1].lower()
    for (key,val) in userDict.items():
        if key == clientName:
            print("This user already exist")
            return
    print("registering")
    print("Got client: " + clientName.lower())
    userDict[clientName.lower()] = [parsedList[2], parsedList[3], 0]
    print(userDict)

#takes out the clients info from the registry
def deRegister(name):
    print("Deregistering")
    userDict.pop(name)
    print(userDict)


def wait_for_DHT_Complete():
    global DHTLeader
    waiting = True
    while waiting:
        msg, addr = serverSocket.recvfrom(2048)
        decodeMSG = msg.decode()
        parsedMSG = decodeMSG.split( )
        print(parsedMessage)
        if parsedMSG[1] == DHTLeader:
            print("DHT complete from the leader")
            serverSocket.sendto("SUCCESS".encode(), (addr))
            waiting = False
        else:
            print("DHT complete sent by someone who is no the leader")
            serverSocket.sendto("FAILURE".encode(), (addr))



#sets up the DHT ring
def dhtSetup(parsedlist, clientADDR):
    print("Setting up the DHT")
    N = int(parsedlist[1])
    if N < 2:
        print("N is not greater than 2")
        serverSocket.sendto("N is not greater than 2".encode(), (clientADDR))
        return
    user = parsedlist[2].lower()
    print("This is the user " + user + "and this is what we looking for " + parsedlist[2].lower())
    if len(userDict) >= N:
        dhtList = {}
        ID = 1
        numberOFUsers = 0
        if user in userDict:
            for (key,val) in userDict.items():
                if numberOFUsers <= N:
                    if user == key:
                        global DHTLeader
                        #append the users ip and ports
                        print("appending users ip and ports")
                        arraryToADD = []
                        DHTLeader = key
                        arraryToADD.append(key)
                        arraryToADD.append(userDict[key][0])
                        arraryToADD.append(userDict[key][1])
                        userDict[key][2] = 2
                        dhtList[0] = arraryToADD
                        numberOFUsers += 2
                        print("Just sent: ")
                        print(userDict)
                        print(arraryToADD)
                    else:
                        print("if the list does not already have n amount add more users")
                        #if the list does not already have n amount add more users
                        arraryToADD = []
                        arraryToADD.append(key)
                        arraryToADD.append(userDict[key][0])
                        arraryToADD.append(userDict[key][1])
                        userDict[key][2] = 1
                        dhtList[ID] = arraryToADD
                        ID += 1
                        numberOFUsers += 1
                        print("Just sent: ")
                        print(arraryToADD)
                else:
                    print("Number of users not enough for DHT")
                    serverSocket.sendto("Not enought users for DHT".encode(), (clientADDR))
                    return
            data = json.dumps({"Table" : dhtList})
            serverSocket.sendto(data.encode(), (clientADDR))
            print("about to send the dhtList")
            print(dhtList)
            dht_setup = True
            wait_for_DHT_Complete()
            #serverSocket.sendto(dhtList.encode(), (clientADDR))   
        else:
            print("user not in table")  
            serverSocket.sendto("User not in table".encode(), (clientADDR))
    else:
        print("not enough in the dict to create dht")
        serverSocket.sendto("Not enough clients registered for N".encode(), (clientADDR))
        


while True:
    message, clientADDR = serverSocket.recvfrom(2048)
    decodedMessage = message.decode().upper()
    parsedMessage = decodedMessage.split( )
    if parsedMessage[0].lower() == "register":
        print("Setting up registration process")
        found = False
        for (x, val) in userDict.items():
            if x == parsedMessage[1]:
                found = True
        if not found:
            register(parsedMessage)
    elif parsedMessage[0].lower() == "deregister":
        userName = parsedMessage[1].lower()
        deRegister(userName)
    elif parsedMessage[0].lower() == "dic":
        print(userDict)
    elif parsedMessage[0].lower() == "setup-dht":
        if dht_setup == False:
            print("ready to set up dht")
            dhtSetup(parsedMessage, clientADDR)
    print(decodedMessage)
    serverSocket.sendto("Recieved registration".encode(), clientADDR)