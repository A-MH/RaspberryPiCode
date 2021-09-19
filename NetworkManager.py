import socket
import time

host, port = "192.168.1.15", 25001
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

while True:
    time.sleep(0.5) #sleep 0.5 sec
    posString = 'message from rpi'
    print(posString)

    sock.sendall(posString.encode("UTF-8")) #Converting string to Byte, and sending it to C#
    receivedData = sock.recv(1024).decode("UTF-8") #receiveing data in Byte fron C#, and converting it to String
    print(receivedData)

def get_commands_str(ID):
    commands = sock.recv(1024).decode("UTF-8")
    subroute = 'lof 1 22-lof 3 23.8-lof 0.05 0-lof 2 0-lof 0.05 0-lof 1 0-lof 0.5 0-lof 0.2 0-lof 0.05 0-lof 0.1 0-lof 0.05 0-\
lof 0.1 0-lof 0.05 0-lof 5 0-lof 0.05 0-'
    return subroute

def send_weight(syringe_weight, deadweight):
    message = f'{syringe_weight}, {dead_weight}'
    sock.sendall(message.encode("UTF-8"))