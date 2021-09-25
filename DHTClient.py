import socket
import sys


def register():
    print("Registering")

stay = True
while stay:
    command = input("Client: ")
    print(str(command))
    if command == "register":
        print("Boutta go to register")
        register()
    elif command == "exit":
        break
    #print("Doing something")


