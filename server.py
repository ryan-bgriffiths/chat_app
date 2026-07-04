# Ryan Griffiths
# ID: 304711836
# csc138-01
# 6/30/2026
# Program:  
#    
# Usage: python server.py <port>

import sys                      #For command line args
from socket import *            #For socket interface
import threading                #For threading interface 
import os                       #For operating sys interface
from datetime import datetime   #For timestamp
import time                     #For time 

#Global Variable to store addresses of registered clients
registeredClients = {} #key = username, value = client socket.

#Create mutex for threading
lock = threading.Lock()

def join(command, client_socket, serverDir):
    """
    Function for JOIN command. 
    Joins a user to the chat server, if not registered JOIN will register 
    the user, already registered users are not re-entered into registration list.
    If the server is at capacity the user will not join and will have to try again later.
    NOTE: join() will conflict with other predifined Python interfaces if utilized.
    """
    #Save username provided
    username = command.split()[1]

    #Protect against race conditions
    with lock:

        #User Already registed -> send response & allow to join
        if username in registeredClients:
            client_socket.send("Already registered, enter next command".encode("ascii"))
            return True
        
        #Server is full -> send response & do not register
        elif len(registeredClients) >= 10:
            client_socket.send("Too Many Users".encode("ascii"))
            return False
        
        #Server has room and new user -> Register and allow to join
        else:
            #Save the address for the user
            registeredClients[username] = client_socket

            #Output status notification in server window
            print(f"{username} Joined the Chatroom")

            #Send confirmation of Joining server to client
            client_socket.send(f"{username} joined! Connected to server!".encode("ascii"))
            
            #Initialize a log folder for the client
            fileName = os.path.join(serverDir, f"{username}.txt")
            with open(fileName, "a"):
                pass
            return True

    return
#End join()

def list(client_socket, username):
    """
    Function for listing all registered users in the chat server.
    client must be a registered user to execute LIST command.
    """

    #If client is not registered return error
    if username is None:
        client_socket.send("Error: Not registered.".encode("ascii"))
    #Return list of current registered users in the chat server
    else:
        listOfClients = ",".join(registeredClients.keys())
        client_socket.send(listOfClients.encode("ascii"))

    return
#End list()

def mesg(command, client_socket, username, serverDir):
    """
    Function for sending an individual message to another registered user.
    Sender and receiver must bother be registered.
    """
    
    # Output status msg to server window & response to client upon 
    #   request to message from an unregistered client
    if username not in registeredClients:
        print("Message request denied: Unregistered sender")
        client_socket.send("Unregistered User\nRegister via command: JOIN <username>".encode("ascii"))
        return
    
    #Split the incoming comman 
    parts = command.split()

    #Verify correct formatting of the MESG command 
    if len(parts) < 3:
        client_socket.send("Error: Invalid format.\nUsage: MESG <username> <message>".encode("ascii"))
        return

    #Store sender and recipient usernames
    sender = username
    recipient = command.split()[1]

    #Store the outgoing message
    message = command.partition(recipient)[2].strip()
    updatedMessage = sender + ": " + message

    #Initializes paths for log files
    senderFile = os.path.join(serverDir, f"{username}.txt")
    recipientFile = os.path.join(serverDir, f"{recipient}.txt")

    #Output status & send notifiction to sender if trying to 
    #   message an unregistered user
    if recipient not in registeredClients:
        print("Message not sent: Unknown recipient")
        client_socket.send("Unknown Recipient".encode("ascii"))
        return 
    #Output status, send message, & log the transaction
    else:
        #Send message to recipient
        destinationSocket = registeredClients[recipient]
        destinationSocket.send(updatedMessage.encode("ascii"))

        #Output status 
        print(f"Message sent to {recipient}")
        client_socket.send(command.encode("ascii"))

        #Store clients info and message to log
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        senderLog = (f"[{timestamp}] INFO: Message sent by {sender} to {recipient} - \"{message}\"")
        recipientLog = (f"[{timestamp}] INFO: Message received by {recipient} from {sender} - \"{message}\"")

        #Write logs to the respective client files
        with open(senderFile, "a") as log:
            log.write(senderLog + "\n")

        with open(recipientFile, "a") as log:
            log.write(recipientLog + "\n")

    return
#End mesg()

def bcst(command, client_socket, username, serverDir):
    """    
    Function for broadcasting a message to all other registered users. 
    """

    #Store the senders username & bcst message
    sender = username
    message = command[4:].strip() 

    #Append the senders username to beginning of message
    updatedMessage = sender + ":" + message 

    #Initialize file path for logging
    senderFile = os.path.join(serverDir, f"{sender}.txt")

    #Output status and send notification to sender if unregistered
    if sender not in registeredClients:
        print("Broadcast denied: Unregistered sender") 
        client_socket.send("Unregistered User\nRegister via command: JOIN <username>".encode("ascii"))
        return 
    
    #Output verification of broadcast 
    client_socket.send((sender + " is sending a broadcast\n" + updatedMessage).encode("ascii"))
    
    #Store information for logging
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    senderLog = (f"[{timestamp}] INFO: Broadcast sent by {sender} - \"{message}\"")

    #Log the broadcast for the sender
    with open(senderFile, "a") as log:
        log.write(senderLog + "\n")

    #Send and log the broadcast for the recipients
    for user, registered in registeredClients.items():
        if user != sender:
            registered.send(updatedMessage.encode("ascii"))
            recipientFile = os.path.join(serverDir, f"{user}.txt")
            recipientLog = (f"[{timestamp}] INFO: Broadcast received by {user} from {sender} - \"{message}\"")
            with open(recipientFile, "a") as log:
                log.write(recipientLog + "\n")

    return
#bcst()

def log(command, client_socket, username, serverDir):
    """
    Function for retreval of all messages sent and received during a client's session. 
    Format: timestamps, sender, receiver (if applicable), and message content.
    """

    #Initialize file path variable for logging
    fileName = os.path.join(serverDir, f"{username}.txt")
    
    #Output status msg & send notification with JOIN instructions 
    #   if the client is not registered.
    if username not in registeredClients:
        print("Message Log denied: Unregistered Client")
        client_socket.send("Unregistered User\nRegister via command: JOIN <username>".encode("ascii"))
        return
    #Read & store the users log file and send the history back.
    else:
        with open(fileName, "r") as log:
            history = log.read()

        client_socket.send(history.encode("ascii"))
        print(f"Chat Log sent for {username}")

    return 
#log()


def threaded(client_socket, serverDir, address):
    """
    Function to handle program threading.
    Responsible for receiving commands from the individual threads. 
    """

    #Variable for username storage
    username = None

    #Set timeout & initialize variable for active user tracking
    client_socket.settimeout(1)
    lastActivity = time.time()
    
    #Enter loop to receive different commands
    while True:

        try:
            
            #Save the response from the client
            data = client_socket.recv(1024)
        
            #Disconnect upon bad response
            if not data:
                print('Disconnecting')
                break

            #Update last activity time 
            lastActivity = time.time()

            #Decode the response to save the entered command
            command = data.decode('ascii').strip()

            #Output verification of receipt
            print(f"Received from {address}: {command}")

            #Close the connection for registered client upon QUIT command
            if command.startswith('QUIT'):

                #Remove the user from list of registered users
                if username in registeredClients:
                    with lock:
                        del registeredClients[username]
                        otherUsers = registeredClients.copy().items()

                    #Output status message in server window
                    print(f"Connection closed for {address}")

                    #Send notification of user leaving to all other registered users
                    for user, registered in otherUsers:
                        try:
                            registered.send(f"{username} left".encode("ascii"))
                        except:
                            pass
                    break
                #Close the connection for unregistered client
                else: 
                    print(f"Connection closed for {address}")
                    break
        
            #Join the chat server if not already registered
            elif command.startswith("JOIN"):
                if not join(command, client_socket, serverDir):
                    client_socket.close()
                    return
                else:
                    username = command.split()[1]

            #List all registered clients in chat server
            elif command.startswith("LIST"):
            
                list(client_socket, username)

            #Message a registered client
            elif command.startswith("MESG"):

                mesg(command, client_socket, username, serverDir)

            #Broadcast a message to all registered clients
            elif command.startswith("BCST"):

                bcst(command, client_socket, username, serverDir)
            
            #List history of all messages sent and received 
            elif command.startswith("LOG"):
            
                log(command, client_socket, username, serverDir)

            #Send error message for invalid commands
            else: 
                client_socket.send("Error: Invalid command.".encode('ascii'))

        #Handle user inactivity
        except timeout:

            #Disconnect the client if inactive for one minute
            if time.time() - lastActivity >= 60:
                print(f"{username}'s session is terminated due to inactivity for 1 minute.")
                client_socket.send("Disconnected due to inactivity.\nGoodbye.".encode("ascii"))
                
                #Remove the client if registered
                if username in registeredClients:
                    with lock:
                        del registeredClients[username]
                
                #Send notification to all registered clients of user disconnection
                for user, registered in registeredClients.items():
                    if user != username:
                        registered.send(f"{username} was disconnected due to inactivity.".encode("ascii"))
                break

        #Handle connection reset if response is not received before disconnection
        except ConnectionResetError:
            print(f"Client {address} disconnected unexpectedly.")

            if username in registeredClients:
                with lock:
                    del registeredClients[username]
            break

        #End while

    #Close the socket and return from the function
    client_socket.close()

    return
#End threaded()


#Function to setup TCP connection
def tcp_server(port):
    """
    Function for the setup of TCP connection used 
    """

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
                print(f"Connected with {address}")

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



def main():
    """
    Main Program Function 
    """

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