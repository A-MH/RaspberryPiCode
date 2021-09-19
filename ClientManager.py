import socket
import time

host, port = "192.168.1.15", 25001
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

ID = '2'

def get_commands():
    receivedData = sock.recv(1024).decode("UTF-8") #receiveing data in Byte fron C#, and converting it to String
    print(f"received: {receivedData}")
    time.sleep(5)
    Send_result(f"message from client {ID}")

def Send_result(result):
    sock.sendall(result.encode("UTF-8")) #Converting string to Byte, and sending it to C#
    get_commands()

sock.sendall(ID.encode("UTF-8")) #Converting string to Byte, and sending it to C#
get_commands()