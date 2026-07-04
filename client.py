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
    """
    Function for receiving messages while client is in the command prompt
    """
    
    #Enter infinite loop for reveiving messages
    while True:
        try:
            response = serverSocket.recv(1024)

            #Exit the program if user Quits and no response is received
            if not response:
                os._exit(0)

            #Output received messages
            print("\n" + response.decode("ascii"))

        except:
            break

    return
#End receiveMessages()

def join(sentence, serverSocket):
    """Function for transmitting JOIN command to server"""
    serverSocket.send(sentence.encode("ascii"))
    return
#End join() 

def list(sentence, serverSocket):
    """Function for transmitting LIST command to server"""
    serverSocket.send(sentence.encode("ascii"))
    return 
#End list()

def mesg(sentence, serverSocket):
    """Function for transmitting MESG command to server"""
    serverSocket.send(sentence.encode("ascii"))
    return
#End mesg() 

def bcst(sentence, serverSocket):
    """Function for transmitting BCST command to server"""
    serverSocket.send(sentence.encode("ascii"))
    return 
#End bcst() 

def log(sentence, serverSocket):
    """Function for transmitting LOG command to server"""
    serverSocket.send(sentence.encode("ascii"))
    return
#End log() 

def main():
    """Main Program Function"""
    
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

    #Create thread for incoming messages
    receiverThread = threading.Thread(target=receiveMessages, args=(serverSocket,))
    receiverThread.daemon = True
    receiverThread.start()

    #Get user input/commands 
    sentence = input("Enter JOIN followed by your username: ").strip()
    
    #Variable for username storage 
    username = None

    #Loop until the user enters QUIT
    while sentence.upper() != "QUIT":
    
        #Handle case where user hits Enter with no input
        if sentence ==  "":
            sentence = input("").strip()
            continue

        #Store the command from the user
        command = sentence.split()[0]

        #Determine & execute the respective function for the given command
        match command.upper():
            case "JOIN":
                #Store the clients username
                username = sentence.split()[1].strip()
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

    #Output status message
    print(f"{username} is quitting the chat server") 

    #Close the connection 
    serverSocket.close()

#End main()

if __name__ == '__main__':
    main()