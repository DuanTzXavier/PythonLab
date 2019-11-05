import socket
import time
import threading

def request_server():
    client_socker = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    request_body = bytes(9999999)
    request_header = "%s" % len(request_body)
    request_data = "%sdata:%s" % (request_header, request_body.decode('utf-8', 'ignore'))
    client_socker.connect(("localhost",8801))
    client_socker.send(bytes(request_data, "utf-8"))
    
    response = client_socker.recv(1024)
    print("request data:", response)
    global timer
    timer = threading.Timer(0.2, request_server)
    timer.start()

if __name__== "__main__":
    timer = threading.Timer(0.2, request_server)
    timer.start()
