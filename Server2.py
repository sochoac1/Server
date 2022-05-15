# ********************************************************************************************
    # Lab: Introduction to sockets
    # Course: ST0255 - Telemática
    # MultiThread TCP-SocketServer
# ********************************************************************************************

# Import libraries for networking communication and concurrency...

from fileinput import filename
import socket
import threading
from typing import final
from urllib import request
import constants
import base64

# Defining a socket object...
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_address = constants.IP_SERVER

def main():
    print("***********************************")
    print("Server is running...")
    print("Dir IP:",server_address )
    print("Port:", constants.PORT)
    server_execution()
    
# Handler for manage incomming clients conections...

def handler_client_connection(client_connection,client_address):
    print(f'New incomming connection is coming from: {client_address[0]}:{client_address[1]}')
    is_connected = True
    while is_connected:
        #Method and file_name b"GET /cover.jpg HTTP/1.1\r\nHost: data.pr4e.org\r\n\r\n"
        request = client_connection.recv(4098260).split(b"\r\n\r\n")
        message = request[0].decode().split(' ') 
        #print(message)
        method = message[0] 
        file_name = message[1] 
        #print('El archivo es:',file_name)
        print(method, file_name, ' HTTP/1.1/ ')
        #GET
        if (method == constants.GET):
            file_name = file_name.lstrip('/')
            #print('Archivo sin:', file_name)
            if(file_name == ''):
                file_name= 'index.html'
            file_name = 'Server/'+file_name
            #print('File name:', file_name) 
            #File exists
            if not(checkFileExistance(file_name)):
                #print('<-------File not found----->')
                header = 'HTTP/1.1 404 Not Found\r\n\r\n'.encode() 
                response = '<html><body>Error 404: File not found</body></html>'.encode('utf-8')                                      
            else:
                file=open(file_name,'rb')
                response=file.read()
                file.close() 
                header = getHeader(file_name)                
            print('Sending ...')
            final_response = header + response
            client_connection.sendall(final_response) 
            print('**********************')
        #POST
        elif(method == constants.POST): 
            complete_file = request[1]   
            #Save file                               
            file=open("./Server/"+file_name, 'wb')
            file.write(complete_file)
            file.close()     
            #Send response  
            response = getHeader(file_name)
            response = response.rstrip(b'\r\n\r\n')
            client_connection.sendall(response)
            print('**********************')
        #HEAD
        elif(method== constants.HEAD):
            file_name = file_name.lstrip('/')
            print('Archivo sin:', file_name)
            if(file_name == ''):
                file_name= 'index.html'
            file_name = 'Server/'+file_name
            if not (checkFileExistance(file_name)):
                #print('<-------File not found----->')
                header = 'HTTP/1.1 404 Not Found\r\n\r\n'.encode() 
            else:
                header=getHeader(file_name)
            header = header.rstrip(b'\r\n\r\n')
            client_connection.sendall(header)
            print('**********************')
        #QUIT
        elif (method == constants.QUIT and file_name=="server"):
            response = '200 BYE\n'
            client_connection.sendall(response.encode(constants.ENCONDING_FORMAT))
            is_connected = False
        else:
            response = '400 BCMD\n\rmethod-Description: Bad method\n\r'
            client_connection.sendall(response.encode(constants.ENCONDING_FORMAT))
    
    print(f'Now, client {client_address[0]}:{client_address[1]} is disconnected...')
    client_connection.close()

#Function to start server process...
def server_execution():
    tuple_connection = (server_address,constants.PORT)
    server_socket.bind(tuple_connection)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print ('Socket is bind to address and port...')
    server_socket.listen(5)
    print('Socket is listening...')
    while True:
        client_connection, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handler_client_connection, args=(client_connection,client_address))
        client_thread.start()
    print('Socket is closed...')
    server_socket.close()

#Mthod to obtain headers
def getHeader(my_file):
     #Identify file extensions
    if(my_file.endswith('.jpg')):
        mimetype='image/jpg'
    elif(my_file.endswith('.css')):
        mimetype='text/css'
    elif(my_file.endswith('.pdf')):
        mimetype='aplication/pdf'
    elif(my_file.endswith('.html')):
        mimetype='text/html'
    elif(my_file.endswith('.mp4')):
        mimetype='video/mp4'
    else:
        header='HTTP/1.1 404 File Not Found'.encode()
        return header        
    
    header='HTTP/1.1 200 OK\n'
    header += 'Content-Type: '+str(mimetype) + "\r\n\r\n"
    response = header.encode('utf-8')
    return response

#Method to find file existance
def checkFileExistance(filePath):
    try:
        with open(filePath, 'r') as f:
            return True
    except FileNotFoundError as e:
        return False
    except IOError as e:
        return False

if __name__ == "__main__":
    main()