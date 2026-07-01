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

#Get user input/commands 
sentence = input("Enter command (LIST, GET filename, QUIT) : ").strip()

#Loop until the user enters QUIT
while sentence.upper() != "QUIT":
    
    #LIST
    if sentence.upper().startswith("LIST"):
        
        #Send the LIST command to the server
        serverSocket.send(sentence.upper().encode('ascii'))

        #Save the response from the server 
        received = serverSocket.recv(1024)

        #Output the returned list of files 
        print("Files on server : ", str(received.decode('ascii')))
   
    #GET     
    elif sentence.upper().startswith("GET"):

        #Save the file name
        parts = sentence.split()
        fileName = parts[1]

        #Send the command to the server
        serverSocket.send((parts[0].upper() + " " + parts[1]).encode('ascii'))

        #Save the response from the server
        response = serverSocket.recv(1024).decode('ascii')

        #Split the response to obtain the file size later
        parts = response.split()

        #Handle a return value of Error
        if response.startswith("Error"):
            print(response)

        else:
            fileSize = int(parts[1])
        
            directory = "client_files"
            
            #Create a directory to store the file if there is not one already
            if not os.path.isdir(directory):
                os.makedirs(directory)

            #Ensure the full path is saved 
            path = os.path.join(directory, fileName)

            #Open a file to write to in binary mode
            with open(path, "wb") as f:
                
                #Track the length of the chuck received 
                received = 0

                #Loop to get all chunks of file 
                while received < fileSize:
                    
                    #Save a file chunk from the server 
                    chunk = serverSocket.recv(1024)
                    
                    #Exit the loop if there is nothing left in the file
                    if not chunk:
                        break
                    
                    #Write the content of the chunk to the file 
                    f.write(chunk)
                    
                    #Increase the count of received 
                    received += len(chunk)

            #Output verification of successful download
            print(f"File '{fileName}' downloaded successfully")

            #Output file path 
            print(f"Saved to: {path}")

    #Handle and output usage upon input of invalid commands 
    else:
        print("Invalid command. Use LIST, GET <filename>, or QUIT.")

    #Prompt for user input        
    sentence = input("Enter command (LIST, GET file, QUIT) : ").strip() 

#Send QUIT to the server if entered by the user
serverSocket.send("QUIT".encode('ascii'))

#Close the connection 
serverSocket.close()

#Output verification of closed connection
print("Connection terminated.")

