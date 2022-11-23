#!/usr/bin/python3
# -*- coding: utf-8 -*-

from socket import *

server_ip = "13.209.85.23"
local_ip = "192.168.0.164"

local_sock = socket(AF_INET, SOCK_STREAM)
local_sock.bind((local_ip, 8080))
local_sock.listen(1)
print("Waiting...")

connectionSocket, addr = local_sock.accept()
print(str(addr), "에서 접속되었습니다.")

data = connectionSocket.recv(1024)
print("받은 데이터 : ", data.decode("utf-8"))

connectionSocket.send("I am a server".encode("utf-8"))
print("메시지를 보냈습니다.")

local_sock.close()