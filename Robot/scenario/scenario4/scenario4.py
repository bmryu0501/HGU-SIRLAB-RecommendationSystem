#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import os

not_question = [1, 4, 5, 6, 7, 8, 10, 12, 15, 16, 17, 19]
dance_sentence = [5, 8]

def talk(i):
  wav_name = "play_" + str(i) + ".wav"
  
  os.system("mpg321 {}".format(wav_name))
  
def play():
  for i in range(1, 20):
    # 또 해볼까?
    if i==9: continue
    
    talk(i)
    
    if i in not_question:
      continue
    else:
      print("Answer: ")
      time.sleep(5)

if __name__ == "__main__":
  play()
