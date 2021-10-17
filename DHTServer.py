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
leaderSocket:int
leaderIP:str
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock = input("What is the socket: ")
serverSocket.bind(('', int(sock)))
registered_users = 0
requested_leave_user:str
print("Dictionary already has: ")
print(userDict)

#registers the inputted clientName/ IPV4 and Ports
def register(parsedList, clientADDR):
    global registered_users
    clientName = parsedList[1].lower()
    for (key,val) in userDict.items():
        if key == clientName:
            print("This user already exist")
            return
    print("registering")
    print("Got client: " + clientName.lower())
    try:
        userDict[clientName.lower()] = [parsedList[2], parsedList[3], 0]
        registered_users += 1
    except:
        serverSocket.sendto("Not enough inputs to register".encode(), (clientADDR))
    print(userDict)

#takes out the clients info from the registry
def deRegister(name):
    data_array = userDict[name]
    if data_array[2] == 0:
        print("Deregister Success")
        userDict.pop(name)
        print(userDict)
        data = json.dumps({"deregister" : "SUCCESS"})
        serverSocket.sendto(data.encode(), (str(data_array[0]), int(data_array[1])))
    else:
        print("Failure deregister")
        data = json.dumps({"deregister" : "FAILURE"})
        serverSocket.sendto(data.encode(), (str(data_array[0]), int(data_array[1])))


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
            print(parsedMSG[1])
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
                print("The number of users is ")
                print(numberOFUsers)
                print('N is ')
                print(N)
                if registered_users >= N:
                    if numberOFUsers <= N:
                        if user == key:
                            global DHTLeader, leaderSocket, leaderIP
                            #append the users ip and ports
                            print("appending users ip and ports")
                            arraryToADD = []
                            DHTLeader = key
                            arraryToADD.append(key)
                            arraryToADD.append(userDict[key][0])
                            print("This is the userdict[key][0]")
                            print(userDict[key][0])
                            leaderIP = userDict[key][0]
                            print("This is what was stored as the leaders IP")
                            print(leaderIP)
                            arraryToADD.append(userDict[key][1])
                            leaderSocket = userDict[key][1]
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

def leave_dht(user):
    global requested_leave_user
    print("passed the user")
    user_found = False
    user_ip:str
    user_sock:int
    for (key,val) in userDict.items():
        print("looking for user")
        print("compareing key  " + str(key) + " with " + user)
        if key == user:
            print("Found user")
            user_val = val
            for (key,val) in enumerate(val):
                if key == 2:
                    if val != 0:
                        user_found = True
                        print("User in dht")
                        requested_leave_user = user_val
                        user_ip = user_val[0]
                        user_sock = user_val[1]
                    else:
                        print("User not in dht")
                        data = json.dumps({"leave" : ["FAILURE"]})
                        serverSocket.sendto(data.encode, (str(user_val[0]), int(user_val[1])))
        elif user_found:
            user_found = False
            users_right_neighbor = val
            data = json.dumps({"leave" : ["SUCCESS", users_right_neighbor]})
            serverSocket.sendto(data.encode(), (str(user_ip), int(user_sock)))
            wait_for_leave_response

                    
         

def wait_for_leave_response():
    print("Waiting for a response")
    msg, addr = serverSocket.recvfrom(2048)
    decodedMessage = msg.decode()


def query_dht(msg, clientADDR):
    global leaderIP, leaderSocket
    print("Recieved a query")
    requested_user = msg[1].lower()
    requested_port = msg[2]
    found = False
    for (key,val) in userDict.items():
        if key == requested_user:
            global leaderIP, leaderSocket
            found = True
            if val[2] == 0:
                #user is free
                print("accepting the query")
                user_IP = val[0]
                user_sock = val[1]
                print("recieved query from: ")
                print(user_IP)
                print(user_sock)
                print("Sending to leader")
                print(clientADDR[0])
                print(requested_port)
                msg_header = "START"
                print("message header " + msg_header)

                data = json.dumps({msg_header : [leaderIP, leaderSocket]})
                serverSocket.sendto(data.encode(), (str(clientADDR[0]), int(requested_port)))
            else:
                #user is in the dht or is the elader
                print("Requested user is in the dht")  
                data = json.dumps({"QUERY-START" : 'FAILURE'})
                serverSocket.sendto(data.encode(), (clientADDR))                  
    if not found:
        print("Query user is not registered")
        print("Sending mess back to ")
        print(clientADDR)
        data = json.dumps({'QUERY-START': "FAILURE"})
        serverSocket.sendto(data.encode(), (clientADDR))
        

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
            register(parsedMessage, clientADDR)
    elif parsedMessage[0].lower() == "deregister":
        userName = parsedMessage[1].lower()
        deRegister(userName)
    elif parsedMessage[0].lower() == "dic":
        print(userDict)
    elif parsedMessage[0].lower() == "setup-dht":
        if dht_setup == False:
            print("ready to set up dht")
            dhtSetup(parsedMessage, clientADDR)
    elif parsedMessage[0].lower() == 'query-dht':
        query_dht(parsedMessage, clientADDR)
    elif parsedMessage[0].lower() == 'leave-dht':
        user = parsedMessage[1].lower()
        print("Starting leave")
        leave_dht(user)
    print(decodedMessage)
    serverSocket.sendto("Recieved registration".encode(), clientADDR)