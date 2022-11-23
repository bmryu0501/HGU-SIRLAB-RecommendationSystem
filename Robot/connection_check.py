#!/usr/bin/python3
# -*- coding: utf-8 -*-

from socket import *

local_ip = "192.168.137.1"

local_sock = socket(AF_INET, SOCK_STREAM)
local_sock.connect((local_ip, 2000))

print("연결 확인됐습니다.")
local_sock.send("저는 파이보 입니다.".encode("utf-8"))

print("메시지를 전송했습니다.")
data = local_sock.recv(1024)

print("받은 데이터 : ", data.decode("utf-8"))
local_sock.close()