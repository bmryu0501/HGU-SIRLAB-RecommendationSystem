import ferFunc as fer

import cv2
import time
import os
import threading

os.environ['KMP_DUPLICATE_LIB_OK']='True'

cap = cv2.VideoCapture(0)
time.sleep(2)

#1. face expression recognition 실행
fer.model_init()

main_fer_thread = threading.Thread(target=fer.fer_thread, args=(cap,), daemon=True)
main_fer_thread.start()
fer.start_timer()

time.sleep(6)

# 놀이 종료를 위해 fer 및 카메라 종료
print("end")
fer.end_timer()

# get emotion_dict after finishing thread
emotion_dict = fer.return_emotion_dict()
print("final emotion dict:", emotion_dict)

print("join...")
# main_fer_thread.join()
print("join done!")
cap.release()
cv2.destroyAllWindows()

time.sleep(5)

# get emotion_dict after finishing thread
emotion_dict = fer.return_emotion_dict()
print("final emotion dict:", emotion_dict)