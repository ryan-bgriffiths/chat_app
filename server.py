# Ryan Griffiths
# ID: 304711836
# csc138-01
# 6/30/2026
# Program:  
#    
# Usage: python server.py <port>

import sys              #For command line args
from socket import *    #For socket interface
import threading        #For threading interface 
import os               #For operating sys interface
from datetime import datetime

#Global Variable to store addresses of registered clients
registeredClients = {} #key = username, value = client socket.

lock = threading.Lock()

def join(command, client_socket, address, serverDir):

    #Obtain the remote address to which the socket is connected 
    address = client_socket.getpeername()

    username = command.split()[1]

    with lock:
        #Already registed - send response 
        if username in registeredClients:
            client_socket.send("Already registered".encode("ascii"))
            return False
        #Server is full - send response 
        elif len(registeredClients) >= 10:
            client_socket.send("Too Many Users".encode("ascii"))
            return False
        else:
            registeredClients[username] = client_socket
            print(f"Registered user-{username}. Address-{address}.")
            client_socket.send(f"User registered as {username}. ".encode("ascii"))
            fileName = os.path.join(serverDir, f"{username}.txt")
            return True

    return

def list(client_socket, username):
    # Registered client only - send a list of all registered clients on individual lines.
    # return the list as a full block. 

    if username is None:
        client_socket.send("Error: Not registered.".encode("ascii"))
    else:
        listOfClients = ""
        for client in registeredClients:
            listOfClients += client + "\n"
        client_socket.send(listOfClients.encode("ascii"))

    return

def mesg(command, client_socket, username, serverDir):
    # Registered client only - client issues MESG <username> 'followed by the message.' to other
    # registered client. Server relays to specified client.
    # Check registration(connection) request from unregistered = "Unregistered User" & JOIN inst. 
    # MESG to unregistered = "Unknown Recipient" back to client. 
    
    sender = username
    recipient = command.split()[1]
    message = command.partition(recipient)[2]
    updatedMessage = sender + ":" + message
    fileName = os.path.join(serverDir, f"{username}.txt")

    if sender not in registeredClients:
        print("Message request denied: Unregistered sender")
        client_socket.send("Unregistered User\nRegister via command: JOIN <username>".encode("ascii"))
        return
    elif recipient not in registeredClients:
        print("Message not sent: Unknown recipient")
        client_socket.send("Unknown Recipient".encode("ascii"))
        return 
    else:
        destinationSocket = registeredClients[recipient]
        destinationSocket.send(updatedMessage.encode("ascii"))
        print(f"Message sent to {recipient}")
        timestamp = datetime.now()
        logMessage = "[" + timestamp + "] INFO:" + message

        with open(fileName, "a") as log:
            log.write(logMessage + "\n")

    return

def bcst(command, client_socket, username, serverDir):
    # Broadcast msg to all other registered & not the sender. Must be reg to complete.

    sender = username
    message = command[4:] #Remove bcst command 
    updatedMessage = sender + ":" + message #append sender username to start of bcst

    if sender not in registeredClients:
        print("Broadcast denied: Unregistered sender") 
        client_socket.send("Unregistered User\nRegister via command: JOIN <username>".encode("ascii"))
        return 
    else:
        for user, registered in registeredClients.items():
            if user != sender:
                registered.send(updatedMessage.encode("ascii"))
    
    return

def log(command, client_socket, address, serverDir):
    # Client retreval of history of all msgs sent and received during thier session. 
    # format: timestamps, sender, receiver (if applicable), and message content.
    # Save per user files as txt. 

    return 

def idleTimer():
    # 1 min idle timer for client, disconnect if no commands received.
    # Release all connected resources(txt) and norify other users in chat. 
    # warning or log msg displayed on server console upon client removal for inactivity.
    return

# Function to handle program threading
# Responsible for receiving commands from the individual threads 
def threaded(client_socket, serverDir, address):

    username = None
    
    #Enter a loop to receive different commands
    while True:
            
        #Save the response from the client
        data = client_socket.recv(1024)
        
        #Disconnect upon bad response
        if not data:
            print('Disconnecting')
            break

        #Decode the response to save the entered command
        command = data.decode('ascii').strip()

        #Output verification of receipt
        print(f"Received from {address}: {command}")

        #Close the connection for registered client upon QUIT command
        if command.startswith('QUIT'):
            if username in registeredClients:
                with lock:
                    del registeredClients[username]
                    print(f"Connection closed for {address}")
                    client_socket.close()
                    return
            else:
                print(f"Connection closed for {address}")
                break
        
        #Join the chat server if not already registered
        elif command.startswith("JOIN"):
            if not join(command, client_socket, address, serverDir):
                client_socket.close()
                return
            else:
                username = command.split()[1]

        #List all registered clients in chat server upon receipt of the LIST command
        elif command.startswith("LIST"):
            
            list(client_socket, username)

        #Message a registered clients
        elif command.startswith("MESG"):

            mesg(command, client_socket, username, serverDir)

        #Broadcast a message to all registered clients
        elif command.startswith("BCST"):

            bcst(command, client_socket, username, serverDir)
            
        #List history of all messages sent and received upon receipt of LOG command
        elif command.startswith("LOG"):
            
            log(command, client_socket, username, serverDir)

        #Send error message for any invalid commands
        else: 
            client_socket.send("Error: Invalid command.".encode('ascii'))

    #End while

    #Close the socket and return from the function
    client_socket.close()

    return
#End threaded()


#Function to setup TCP connection
def tcp_server(port):

    #Create TCP socket
    server_socket = socket(AF_INET, SOCK_STREAM)

    #Bind to all interfaces on port provided
    server_socket.bind(("0.0.0.0", port))

    #Set socket to listen 
    server_socket.listen(6)

    #Set timeout time (1sec)
    server_socket.settimeout(1)

    #Output verification of running server
    print(f"Server running on 0.0.0.0:{port}")

    #Check the direcory path and save to variable
    serverDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server_files")
   
    #Output notification of file directory 
    print(f"Serving files from directory: {serverDir}")

    #Try to connect to a client
    try:
        #Enter an infinite loop to wait for clients to connect
        while True:
            #Wait for a client to connect
            try:
                #Save socket and address of newly connected client 
                client_socket, address = server_socket.accept()

                #Output verification of connected client 
                print(f"Connected by {address}")

                #Create a thread for the client and pass the client's socket 
                thread1 = threading.Thread(target = threaded, args=(client_socket, serverDir, address))
                
                #Start the new thread and handoff, then loop to wait for another client
                thread1.start()

            #Upon timeout loop back and wait for a client
            except timeout:
                continue     

    #Catch keyboard interrupts and handle
    except KeyboardInterrupt:
        pass

    #Close the socket
    finally:
        server_socket.close()

    return
#End tcp_server()


#Main program function
def main():
    
    #Validation of comman line arguments provided, output usage upon descrepency
    if len(sys.argv) != 2:
        print("Usage: python server.py <port number>")
        sys.exit(1) 

    #Save the provided port number from the user 
    port = int(sys.argv[1])
    
    #Try to setup the tcp connection
    try:
        tcp_server(port)
    #Handle interrupts and shutdown the server/end the program
    except KeyboardInterrupt:
        pass

    sys.exit(0)
#End main()

if __name__ == '__main__':
    main()