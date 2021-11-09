import socket
import time

ID = 1
host, port = "192.168.1.15", 25001

def setup_connection(in_ID):
    global ID
    global sock
    ID = in_ID
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.sendall(f"{ID}".encode("UTF-8")) #initially, we need to send the client ID

def get_commands():
    global sock
    global ID
    commands_str = ''
    commands_str = sock.recv(1024).decode("UTF-8") #receiveing data in Byte from C#, and converting it to String
    while commands_str == '': # if received string is empty, it could mean the connection is lost. it could have other causes which I may not be aware of
        print("connection seems to be lost, trying to reconnect...")
        sock.close()
        setup_connection(ID) # try restablishing connection

    print(f"received: {commands_str}")
    return commands_str

def send_result(result):
    sock.sendall(result.encode("UTF-8")) #Converting string to Byte, and sending it to C#
    print("message sent")
    
