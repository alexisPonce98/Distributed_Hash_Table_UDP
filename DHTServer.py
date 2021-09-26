import socket
#need to figure out this part

clientName:str
state:int# 0 = free, 2 = inDHT, 3 = Leader
userDict = {}

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock = input("What is the socket: ")
serverSocket.bind(('', int(sock)))

def register(parsedList):
    print("registering")
    clientName = parsedList[1]
    print("Got client: " + clientName)
    userDict[clientName] = [parsedList[2], parsedList[3], 0]
    print(userDict)

while True:
    message, clientADDR = serverSocket.recvfrom(2048)
    decodedMessage = message.decode().upper()
    print(decodedMessage)
    serverSocket.sendto("Recieved registration".encode(), clientADDR)