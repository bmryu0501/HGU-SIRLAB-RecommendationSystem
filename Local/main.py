"""
Created on Mon Nov 21 2022
@author: shimgahyeon

This program works in Local. 
"""
from FER import ferFunc as fer
from SpeechRecognition import srFunc as sr
from EyeGaze import eyegazeFunc as eyegaze
import ERmodel
import cal_scores as cal
# import makeFolder as mfd

from socket import *
import cv2
import playsound
import threading
import time
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

### User Info ###
UID = None
CID = None
TID = None

### Reommendation ###
recommendations = []
recom_num = 2

### Evaluation Score ###
parent_score = None
expert_score = None

### Engagement level ###
engagement_level = None
level_dict = {"VERYHIGH":100, "HIGH":75, "LOW":50, "VERYLOW":25}

### socket info ###
serv_ip = "13.209.85.23"
serv_port = 8080
local_ip = "192.168.137.92"
local_port = 2000

# '''
print('''\\n
##################
# Before Playing #
##################''')
'''
0. socket setting (robot, server)
'''
### open socket for robot
global local_socket
local_socket = socket(AF_INET, SOCK_STREAM) #IPv4 protocol, TCP type socket object
#to handle "Address already in use" error
local_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
print("Wait for connection with robot...")

### connect to robot
#bind host and port
local_socket.bind((local_ip, local_port))
local_socket.listen()
robot_socket, addr = local_socket.accept()
print("Connect to Robot!")

'''
1. Receive UID and "start" signal from robot
'''
# receive message from robot
message = robot_socket.recv(65535)
message = message.decode()
message = message.split(' ')


if len(message) != 2:
    print(f"[Error] Cannot store UID and signal. Received message is {message}.")
    exit(-1)
else:   
    UID, signal = message
    print("Receive UID and 'start' signal from Robot.")


"""
2. Receive the result of recommendation(list of TIDs) from server
"""
# connect to server
serv_sock = socket(AF_INET, SOCK_STREAM)
serv_sock.connect((serv_ip, 8080))
print("\tConnect to Server")

### 2-1. send UID to server and request TID from server 
# format: "recommend UID"
message = "recommend " + str(UID) # local --> server
# send
serv_sock.send(message.encode())
print("\tSend message to Server to request recommend for user " + UID)

### 2-2. receive PlayID from server and store it
# recv message from server
message = serv_sock.recv(65535)
message = message.decode('utf-8')
print(f"\tReceive recommendation: {message} from Server")

# message parsing
message = message.split(' ')
recommendations = message # recommendations = [TID, TID ...]

### 2-3. close serv socket 
serv_sock.close()
print("\tDisconnect server...")

"""
3. Request user to choice play 
"""
message = "choice" # local --> robot
robot_socket.send(message.encode())
recommendations = [4]
TID = input(f"Select Play among {recommendations}: ")
print("Send 'choice' signal to Robot.")


"""
5. send PlayID to robot
"""
message = str(TID)
robot_socket.send(message.encode())
print(f"Send TID({TID}) to Robot.")
print('''\\n
##################
#### Playing #####
##################''')

"""
1. start FER thred
"""
cap = cv2.VideoCapture(0)
time.sleep(2)

fer.model_init()

main_fer_thread = threading.Thread(target=fer.fer_thread, args=(cap,), daemon=True)
main_fer_thread.start()
fer.start_timer()

q_num = 0
done = 0

audio_filename = UID + "_audio"; answer_filename = UID + "_reply"

"""
playing...
"""
while not done:
    ###  2. Robot request "q_num reply"    
    # recv message "reply" or "end"
    message = robot_socket.recv(65535)
    message = message.decode()
    message = message.split(' ')

    if len(message) == 2:
        q_num = message[0]
        sr.reply(cap, q_num, audio_filename, answer_filename)
       
    ### 3. Receive "end" message from robot
    elif message[0] == "end":
        done = 1
    else:
        print(f"[Error] message is not 'record' or 'end'.\nmessage = '{message}'")


print("Play Done!")
robot_socket.close()

print('''\\n
##################
# After Playing ##
##################''')

'''
join thread
'''
fer.end_timer()
# main_fer_thread.join()

cap.release()
cv2.destroyAllWindows()

'''
1. calculate scores and get engagement level
'''
# get results
total_reply = sr.get_reply_list()
total_eye_gaze = sr.get_eye_gaze_list()
total_emotion_dict = fer.get_emotion_dict()
print("total reply:", total_reply)
print("total eye gaze:", total_eye_gaze)
print("total emotion:", total_emotion_dict)
print()

print("Calculate scores...")
parent_score, expert_score = input("The evaluation score of parent and expert(0~100):")
print("### Achievement ###")
print("parent score:", parent_score)
print("expert score:", expert_score)
print()

print("### Engagement ###")
total_reply_score, total_eye_gaze_score, total_emotion_score, engagement_score = cal.calculate_total_score(0, UID, CID, TID, total_reply, total_eye_gaze, total_emotion_dict)
print("total reply score:", total_reply_score)
print("total eye gaze score:", total_eye_gaze_score)
print("total emotion score:", total_emotion_score)
print("--> engagement score:", engagement_score)
print()

print("ER model")
engagement_level = ERmodel.get_level(engagement_score)
print("engagement level:", engagement_level)
print()

'''
2. send all the data to server
'''
serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv_sock.connect((serv_ip, 8080))

# send data of evaluation
message = "update achievement " + str(CID) + " " + str(TID) + " " + str(parent_score) + " " + str(expert_score)
serv_sock.send(message.encode())
# send data of engagement
message = "update engagement " + str(CID) + " " + str(TID) + " " + str(engagement_score) + " " + str(level_dict[engagement_level])
serv_sock.send(message.encode())

serv_sock.close()

print("Play is entirely end! Thank you.")