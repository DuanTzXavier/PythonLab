# coding:utf-8
import socket
import time
from multiprocessing import Process
import threading
import os

RECEIVE_SIZE = 1024
BIT_SIZE = 8
KB_SIZE = RECEIVE_SIZE * BIT_SIZE
MB_SIZE = RECEIVE_SIZE * RECEIVE_SIZE * BIT_SIZE
GB_SIZE = RECEIVE_SIZE * RECEIVE_SIZE * RECEIVE_SIZE * BIT_SIZE

AVG_SPEED = 0

IS_INIT = False

speeds = []

error_times = 0

def handle_client(client_socket, speeds):
    start_time = time.time()

    # 获取客户端请求数据
    request_data = client_socket.recv(RECEIVE_SIZE)
    responseString = request_data.decode('utf-8','ignore')
    index = responseString.find("data:")
    length = responseString[0: index]
    length = len(length) + int(length)
    times = 1
    while times * RECEIVE_SIZE < length:
        request_data = client_socket.recv(RECEIVE_SIZE)
        responseString += request_data.decode('utf-8','ignore')
        times += 1
    # print("request data:", responseString)
    
    cost_time = time.time() - start_time
    speed = length / cost_time / 8

    speedText = getSpeedText(speed)

    global error_times
    if IS_INIT and AVG_SPEED > 0 and (AVG_SPEED * 0.8) > speed:
        print("Waning !!! speed is too low!! speed:", speedText)
        print("request data size:", length)
        print("request data time cost:", cost_time)
        print("request data speed: ", speedText)
        error_times += 1
    else:
        error_times = 0

    global os
    if error_times > 2:
        # 发送
        os.system('say "发送Email!"')
    elif error_times > 1:
        os.system('say "Warning!"')

    

    # 构造响应数据
    response = "request data speed:" + speedText
    # print("response data:", response)

    # 向客户端返回响应数据
    client_socket.send(bytes(response, "utf-8"))
    
    client_socket.close()

    # global speeds

    if(not IS_INIT):
        speeds.append(speed)


    

def init_avg_speed():
    global IS_INIT
    global timer
    global speeds

    if len(speeds) == 0 : 
        timer = threading.Timer(10, init_avg_speed)
        timer.start()
        return

    allSpeed = 0
    for _, val in enumerate(speeds):
        allSpeed += val

    global AVG_SPEED
    AVG_SPEED = allSpeed / len(speeds)

    if AVG_SPEED <= 0:
        IS_INIT = False
        timer = threading.Timer(10, init_avg_speed)
        timer.start()
        print("error avg speed: ", getSpeedText(AVG_SPEED))
    else:
        IS_INIT = True
        print("avg speed: ", getSpeedText(AVG_SPEED))

def getSpeedText(speed):
    speedText = ""
    if(int(speed) > GB_SIZE):
        speed = speed / GB_SIZE
        speedText = "%sG/s" % speed
    elif (int(speed) > MB_SIZE):
        speed = speed / MB_SIZE
        speedText = "%sM/s" % speed
    elif (speed > KB_SIZE):
        speed = speed / KB_SIZE
        speedText = "%sK/s" % speed
    else:
        speedText = "%sbit/s" % speed

    return speedText


if __name__== "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", 8801))
    server_socket.listen(9999)

    timer = threading.Timer(5, init_avg_speed)
    timer.start()
    while True:
        client_socket, client_address = server_socket.accept()
        # print("[%s, %s]用户连接上了" % client_address)
        handle_client_process = threading.Thread(target=handle_client, args=(client_socket, speeds,))
        handle_client_process.start()