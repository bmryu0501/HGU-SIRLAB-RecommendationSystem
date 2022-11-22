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
import makeFolder as mfd

from socket import socket
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

# '''
print('''\
##################
# Before Playing #
##################''')
# '''
# global serv_socket, robot_socket
# host = ""; port = 5000


# '''
# 0. socket setting (robot, server)
# '''
# ### initialize serv sock
# #IPv4 protocol, TCP type socket object
# serv_socket = socket(socket.AF_INET, socket.SOCK_STREAM)
# #to handle "Address already in use" error
# serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


# ### open socket for robot


# ### connect to robot

# '''
# 1. Receive UID and "start" signal from robot
# '''
# # receive from robot

# # message parsing
# message = message.split(' ')
# recommendations = message

# ### 2. receive UID with "start message" from robot and store it
# if len(message) != 2:
#     print(f"[Error] Cannot store UID and signal. Received message is '{message}'.")
#     exit(-1)
# else:   
#     UID, signal = message


# """
# 2. Receive the result of recommendation(list of TIDs) from server
# """
# # bind host and port
# serv_socket.bind((host, port))
# # server allows a maximum of 5 queued connections
# serv_socket.listen(5)
# client_socket, addr = serv_socket.accept()

# ### 2-1. send UID to server and request TID from server 
# # format: "recommend UID"
# message = "recommend " + str(UID) # local --> server
# # send

# ### 2-2. receive PlayID from server and store it
# # recv message from server
# user = client_socket.recv(65535) # 65535는 뭐지?! # local <-- server
# message = user.decode()

# # message parsing
# message = message.split(' ')
# recommendations = message

# ### 2-3. close serv socket 

# """
# 3. Request user to choice play 
# """
# message = "choice" # local --> robot
# # 로봇에서 골라줄래~ 나옴
# TID = input(f"Select Play among {recommendations}: ")


# """
# 5. send PlayID to robot
# """


print('''\
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
    ###  2. Robot request "reply"    
    # signal
    # recv message "reply" or "end"
    if message == "reply":
        sr.reply(cap, q_num, audio_filename, answer_filename)
        q_num += 1
    ### 3. Receive "end" message from robot
    elif message == "end":
        done = 1
    else:
        print(f"[Error] message is not 'record' or 'end'.\nmessage = '{message}'")

print("Play Done!")

print('''\
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

'''
3. socket close (robot, server)
'''


print("Play is entirely end! Thank you.")