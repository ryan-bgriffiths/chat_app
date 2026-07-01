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

# Function to handle program threading
# Responsible for receiving commands from the individual threads 
def threaded(client_socket, serverDir, semaphore):

    try:
        #Enter a loop to receive different commands
        while True:

            #Save the response from the client
            data = client_socket.recv(1024)
        
            #Disconnect upon bad response
            if not data:
                print('Disconnecting')
                break

            #Decode the response to save the entered command
            command = data.decode('ascii')

            #Obtain the remote address to which the socket is connected 
            address = client_socket.getpeername()

            #Output verification of receipt
            print(f"Received from {address}: {command}")

            #Close the connection if the client sends the QUIT command
            if command.startswith('QUIT'):
                print(f"Connection closed for {address}")
                break

            #List all files in the directory upon receipt of the LIST command
            elif command.startswith("LIST"):
            
                #Save the list of names returned of the entries in the directory 
                files = os.listdir(serverDir)

                #Send a list of all files in the directory to the client
                client_socket.send(", ".join(files).encode('ascii'))
            
            #Read the specified file upon receipt of the GET command 
            elif command.startswith("GET"):
            
                #Split the received command to separate the file name 
                parts = command.split() 
                fileName = parts[1]

                #Ensure the full file path is saved
                path = os.path.join(serverDir, fileName)

                #Validate the file path is within the directory
                if os.path.isfile(path) != True:

                    #Output an error message if the file is not found
                    message = f"Error : File {fileName} not found."
                    client_socket.send(message.encode('ascii'))
            
                #Read from the specified file
                else:
                    #Send confirmation along with file size to the client 
                    message = "Okay " + str(os.path.getsize(path))
                    client_socket.send(message.encode('ascii'))

                    #Open the file to read in binary mode 
                    f = open(path, "rb")
                
                    #Read chunks from the file and send to the client until eof 
                    while True:
                        #Binary mode
                        chunk = f.read(1024)
                        if not chunk:
                            break
                        client_socket.sendall(chunk)
                
                    #Close the file 
                    f.close()

                    #Output verification of sent file 
                    print(f"Sent file '{fileName}' to {address}")   

            #Send error message for any invalid commands
            else: 
                client_socket.send("Error: Invalid command.".encode('ascii'))

        #End while

    finally:
        semaphore.realease() 
    
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
        semaphore = threading.Semaphore(10)

        #Enter an infinite loop to wait for clients to connect
        while True:
            #Wait for a client to connect
            try:
                #Save socket and address of newly connected client 
                client_socket, address = server_socket.accept()

                #Output verification of connected client 
                print(f"Connected by {address}")

                if semaphore.acquire(blocking = False):
                    #Create a thread for the client and pass the client's socket 
                    thread1 = threading.Thread(target = threaded, args=(client_socket, serverDir, semaphore))
                    #Start the new thread and handoff, then loop to wait for another client
                    thread1.start()
                else:
                    client_socket.send("Server full.")
                    client_socket.close()

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