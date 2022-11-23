#!/usr/bin/python3
# -*- coding: utf-8 -*-

from socket import *
import os

### Socket Info ###
local_ip = "192.168.137.1"
port = 2000

### User Info ###
UID = None
CID = None
TID = None

scenario_path = './scenario/'

print('''\
##################
# Before Playing #
##################''')
'''
0. Local socket에 접속
'''
local_sock = socket(AF_INET, SOCK_STREAM)
local_sock.connect((local_ip, port))
print("로컬과의 연결을 확인했습니다.")

'''
1. UserInfo.txt에서 UID, username 저장
'''
f = open("UserInfo.txt", "r")
info = f.readline()
info = info.split(",")
UID = info[1]
username = info[0]
f.close()

'''
2. Local에 "UID start" signal 전송
'''
local_sock.send((str(UID) + " start").encode("utf-8"))
print("메시지를 전송했습니다.")

'''
3. Local에서 "choice" 들어오면 로봇이 "하고 싶은 놀이를 춤추는 유령 놀이랑 빨래집게 놀이 중에 골라줘. 다 고른 후에 고른 놀이를 나에게 말해줘" 실행
'''
data = local_sock.recv(1024)
message = data.decode("utf-8")
if message == "choice":
    os.system("mpg321 {}".format("choice.wav"))

'''
4. Receive TID from Local
'''
data = local_sock.recv(1024)
TID = data.decode("utf-8")

print('''\
##################
#### Playing #####
##################''')

'''
시나리오 실행
'''

task_path = scenario_path + 'scenario'+TID

# from import or os.chdir() 이동


print('''\
##################
# After Playing ##
##################''')
'''
1. send "end" signal to local
'''


'''
2. socket close()
'''
local_sock.close()