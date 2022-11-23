#!/usr/bin/python3
# -*- coding: utf-8 -*-

from socket import *

UID = "001"
local_ip = "192.168.0.164"

clnt_sock = socket(AF_INET, SOCK_STREAM)
clnt_sock.connect((local_ip, 8080))

print("연결 확인됐습니다.")
clnt_sock.send((UID+"/start").encode("utf-8"))

print("메시지를 전송했습니다.")
data = clnt_sock.recv(1024)

print("받은 데이터 : ", data.decode("utf-8"))
clnt_sock.close()