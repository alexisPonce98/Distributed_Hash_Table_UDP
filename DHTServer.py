from os import name
import socket
#need to figure out this part

clientName:str
state:int# 0 = free, 2 = inDHT, 3 = Leader
userDict = {}
dht_setup = False
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock = input("What is the socket: ")
serverSocket.bind(('', int(sock)))
print("Dictionary already has: ")
print(userDict)
def register(parsedList):
    print("registering")
    clientName = parsedList[1]
    print("Got client: " + clientName.lower())
    userDict[clientName.lower()] = [parsedList[2], parsedList[3], 0]
    print(userDict)

def deRegister(name):
    print("Deregistering")
    userDict.pop(name)
    print(userDict)

def dhtSetup(parsedlist, clientADDR):
    print("Setting up the DHT")
    N = parsedlist[1]
    if N < 2:
        print("N is not greater than 2")
        serverSocket.sendto("N is not greater than 2".encode(), (clientADDR))
        return
    user = parsedlist[2]
    if len(userDict) >= N:
        for (key,val) in userDict.items():
            if userDict[key] == user:
                userFound = True
                for (key,val) in user[key]:
                    print("alter the tuples state variable")
        if not userFound:
            print("couldnt find the user")
            return
        else:
            print("user was found")
            secondTuple = userDict[userName]
    else:
        print("not enough in the dict to create dht")
        


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
    elif parsedMessage[0].lower == "setup-dht":
        if not dht_setup:
            dhtSetup(parsedMessage, clientADDR)
    print(decodedMessage)
    serverSocket.sendto("Recieved registration".encode(), clientADDR)