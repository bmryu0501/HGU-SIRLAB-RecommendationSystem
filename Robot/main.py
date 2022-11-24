#!/usr/bin/python3
# -*- coding: utf-8 -*-

from socket import *
import os

### Socket Info ###
local_ip = "192.168.137.92"
port = 2000

### User Info ###
UID = None
CID = None
TID = None

scenario_path = './scenario'

print('''\
##################
# Before Playing #
##################''')
'''
0. Local socket에 접속
'''
local_sock = socket(AF_INET, SOCK_STREAM)
local_sock.connect((local_ip, port))
print("Connect to local.")

'''
1. UserInfo.txt에서 UID, username 저장
'''
f = open("UserInfo.txt", "r")
info = f.readline()
info = info.split(",")
username = info[0]
UID = info[1]
f.close()

'''
2. Local에 "UID start" signal 전송
'''
message = str(UID) + " start"
local_sock.send(message.encode())
print(type(message), message)

'''
3. Local에서 "choice" 들어오면 로봇이 "하고 싶은 놀이를 춤추는 유령 놀이랑 빨래집게 놀이 중에 골라줘. 다 고른 후에 고른 놀이를 나에게 말해줘" 실행
'''
data = local_sock.recv(1024)
message = data.decode("utf-8")
if message == "choice":
    os.system("mpg321 {}".format("choice.wav"))
    print("Receive 'choice' signal.")

'''
4. Receive TID from Local
'''
data = local_sock.recv(1024)
TID = data.decode("utf-8")
print("Receive TID")

print('''\
##################
#### Playing #####
##################''')

'''
시나리오 실행
'''
TID = '/scenario' + TID                 # scenario4
task_path = scenario_path + TID         # ./scenario/scenario4
text_path = task_path + TID + ".txt"    # ./scenario/scenario4/scenario4.txt

'''
1. scenario4.txt에서 total_question_number, not_question 저장
'''
f = open(text_path, "r")
info = f.readline()
total_question_number = int(info)

info = f.readline()
info = info.split(",")
not_question = info
f.close()

'''
2. 놀이 실행 --> 질문 마다 Local에 video 및 질문 시작 signal 전송
'''
for i in range(1, total_question_number+1):
    if i == 9: continue
    
    wav_name = task_path + "/play_" + str(i) + ".wav"
    os.system("mpg321 {}". format(wav_name))
    
    if i in not_question:
        continue
    else:
        local_sock.send((str(i) + " reply").encode("utf-8"))
        print("Send 'reply' signal.")
        
        message = local_sock.recv(1024)
        message = message.decode("utf-8")

print('''\
##################
# After Playing ##
##################''')
'''
1. send "end" signal to local
'''
local_sock.send("end".encode("utf-8"))
print("Send 'end' signal.")

'''
2. socket close()
'''
local_sock.close()
print("Disconnect to local...")