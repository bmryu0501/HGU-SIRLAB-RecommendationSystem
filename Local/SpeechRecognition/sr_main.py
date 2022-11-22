import cv2 
import playsound
import threading
import time
import os

import srFunc as sr

audio_filename = "UID_audio"
answer_filename = "UID_reply"

cap = cv2.VideoCapture(0)

sr.reply(cap, 1, "001", answer_filename)

sr.reply(cap, 2, audio_filename, answer_filename)

total_reply = sr.get_reply_list()
total_eyegaze = sr.get_eye_gaze_list()

print(total_reply)
print(total_eyegaze)