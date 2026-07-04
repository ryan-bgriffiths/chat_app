# Ryan Griffiths
# ID: 304711836
# csc138-01
# 6/27/2026
# Program:
#   
# Usage : python<3> client.py <address> <port>

from socket import *    #For socket interface 
import sys              #For command line args 
import os               #For operating sys interface 
import threading 

def receiveMessages(serverSocket):
    while True:
        try:
            response = serverSocket.recv(1024)

            if not response:
                os._exit(0)
                break

            print(response.decode("ascii"))

        except:
            break

    return

def join(sentence, serverSocket):
    serverSocket.send(sentence.encode("ascii"))
    return

def list(sentence, serverSocket):
    serverSocket.send(sentence.encode("ascii"))
    return 

def mesg(sentence, serverSocket):
    serverSocket.send(sentence.encode("ascii"))
    return

def bcst(sentence, serverSocket):
    serverSocket.send(sentence.encode("ascii"))
    return 

def log(sentence, serverSocket):
    serverSocket.send(sentence.encode("ascii"))
    return

def main():
    
    #Validate command line argument provided, output usage upon discrepency and exit 
    if len(sys.argv) != 3:
        print("Usage: python client.py <Address> <Port Number>")
        sys.exit(1)

    #Save the provided server name 
    serverName = sys.argv[1]

    #Save the provided port number 
    serverPort = int(sys.argv[2])

    #Setup the socket and try to connect to the server
    serverSocket = socket(AF_INET, SOCK_STREAM)

    try:
        serverSocket.connect((serverName,serverPort))
        print(f"Connected to server {serverName}:{serverPort}")
    #Handle if unable to connect
    except:
        print("Could not connect to the server.")
        sys.exit(1)

    receiverThread = threading.Thread(target=receiveMessages, args=(serverSocket,))
    receiverThread.daemon = True
    receiverThread.start()

    #Get user input/commands 
    sentence = input("Enter JOIN followed by your username: ").strip()

    #Loop until the user enters QUIT
    while sentence.upper() != "QUIT":
    
        if sentence ==  "":
            sentence = input("").strip()
            continue

        command = sentence.split()[0]

        match command.upper():
            case "JOIN":
                join(sentence, serverSocket)
            case "LIST":
                list(sentence, serverSocket)
            case "MESG":
                mesg(sentence, serverSocket)
            case "BCST":
                bcst(sentence, serverSocket)
            case "LOG":
                log(sentence, serverSocket)
            case _: #Default-invalid command
                print("Invalid command. Use JOIN <username>, LIST, MESG <username> <message>," \
                "BCST <message>, LOG, or QUIT.")

        #Prompt for user input        
        sentence = input("").strip() 

    #Send QUIT to the server if entered by the user
    serverSocket.send("QUIT".encode('ascii'))

    #add received quit message and output then close the connection

    #Close the connection 
    serverSocket.close()

#End main()

if __name__ == '__main__':
    main()