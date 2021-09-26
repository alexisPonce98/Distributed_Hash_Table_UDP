import socket
import sys

processName:str
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverIP:int
serverSocket:int

#register long_name IP port(s)
def register(parsedList):
    print("Registering")
    processName = parsedList[1]
    print("This is the second input: " + parsedList[1])
    clientSocket.sendto(parsedList.encode(), (serverIP, serverSocket))


def deRegister(cmd):
    print("Going to deregister")
    clientSocket.sendto(cmd.encode(), (serverIP, int(serverSocket)))

def showData():
    clientSocket.sendto("dic".encode(), (serverIP, int(serverSocket)))

def dhtSetup(cmd):
    clientSocket.sendto(cmd.encode(), (serverIP, int(serverSocket)))

wait = False
while True:
    while wait:
        message, serverADDR = clientSocket.recvfrom(2048)
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
        dhtSetup()
    elif parsed[0] == "dic":
        showData(command)
    elif command == "exit":
        break
    #print("Doing something")


