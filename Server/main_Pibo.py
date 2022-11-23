import socket
import argparse

ip_adress = '13.209.85.23'
port = 8080

def update():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((ip_adress, port))

    sock.send("update 12 achievement 0 2 90 90".encode())

    # listen to server
    data = sock.recv(65535)
    print(data.decode())

    sock.close()

def recommend():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((ip_adress, port))

    sock.send("recommend 12".encode())

    # listen to server
    data = sock.recv(65535)
    print(data.decode())

    sock.close()

if __name__ == '__main__':
    while True:
        command = input('command: ')
        if command == 'update':
            update()
        elif command == 'recommend':
            recommend()
        else:
            print('command is not recommend or update')
            exit()