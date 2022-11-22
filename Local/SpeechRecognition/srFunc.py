import time
import sys
import os
#1. settings for recorder
import queue, threading
import sounddevice as sd  #  <-- 
import soundfile as sf    #  <-- 이거 2개는 pip install로 다운 받아야 함
import librosa
#2. settings for kakaoSTT
import requests
import json

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from EyeGaze import eyegazeFunc as eg

kakao_url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"
key = '66a0a3d659eecc18f51e89741464b6b1'
kakao_headers = {
    "Content-Type": "application/octet-stream",
    "X-DSS-Service" : 'DICTATION',
    "Authorization": "KakaoAK " + key
}

#3. settings for CLOVA sentiment analysis
client_id = "fj2m6ajic8"
client_secret = "21KfXGic084COIH00zE4VByOhFieaZRwbH2qaYds"
url="https://naveropenapi.apigw.ntruss.com/sentiment-analysis/v1/analyze"
headers = {
    "X-NCP-APIGW-API-KEY-ID": client_id,
    "X-NCP-APIGW-API-KEY": client_secret,
    "Content-Type": "application/json"
}

q = queue.Queue()
recorder = False
recording = False

textpath = ""
audiopath = ""
answerpath = ""

# format of speech and eye gaze dict
speech_dict = dict(q_num = 0, reply_score = 0, answers = "")
eye_gaze_dict = dict(q_num = 0, eye_gaze_frame = 0, total_frame = 0, eye_gaze_score = 0) # ** add key 'eye gaze score'
# log of speech and eye gaze dict
total_reply = []
total_eye_gaze = []

# 음성 녹음을 시작하고 soundfile에 음성 정보를 저장함
def complicated_record():
    # global 변수 호출
    global audiopath
    
    # 정해진 audiopath에 음성 녹음 파일 생성 후 음성 녹음 상태(recording)이 True일 동안 녹음
    with sf.SoundFile(audiopath, mode='w', samplerate=16000, subtype='PCM_16', channels=1) as file:
        with sd.InputStream(samplerate=16000, dtype='int16', channels=1, callback=complicated_save):
            while recording:
                file.write(q.get())

# 복사한 음성 정보를 q(queue)에 저장
def complicated_save(indata, frames, time, status):
    # indata의 사본을 q에 저장
    q.put(indata.copy())

# global 'recorder' 변수를 실행시켜 음성 녹음을 시작함
def start():
    # global 변수 호출
    global recorder
    global recording
    
    # '음성 녹음 중임(True)'로 전환 후 음성 녹음 시작
    recording = True
    recorder = threading.Thread(target=complicated_record)
    print('start recording')
    recorder.start()
    
# global 'recorder' 변수를 중지시켜 음성 녹음을 정지함
def stop():
    
    # global 변수 호출
    global recorder
    global recording
    
    # '음성 녹음 상태가 아님(False)'로 전환 후 음성 녹음 중단
    recording = False    
    recorder.join()
    print('stop recording')
    
# 음성 녹음을 시작하고 'time_sec'만큼 대기 후 종료
def record():
    start()
    time.sleep(5)
    stop()

# 저장된 음성 파일에 대해 음성-텍스트 변환을 거친 후 결과 문자열을 textpath file에 저장
# Kakao Speech-to-Text(STT) api 활용 
def STT():
    # global 변수 호출
    global textpath
    global answerpath
    
    # 0 ~ 5초 사이로 resample된 음성 파일을 호출 후 읽어들임
    with open("./resample.wav", 'rb') as fp:
        audio = fp.read()

    # Kakao STT api 실행(response)
    response = requests.post(kakao_url, headers=kakao_headers, data=audio)
    
    # STT를 마친 텍스트를 추출 후 json 문자열을 python 객체로 변환(loads)
    result = response.text[response.text.index('{"type":"finalResult"'): response.text.rindex('}')+1]
    result = json.loads(result)
    
    # 결과 확인용 print
    # print(result['value'])

    # STT를 마친 텍스트를 textpath와 answerpath에 저장
    f = open(textpath, 'a')
    f.writelines(result['value'] + " ")
    f.close()
    
    f = open(answerpath, "a")
    f.writelines(result['value'] + " ")
    f.close()

    return result['value']


# 저장된 텍스트에 대한 감성 분석을 실시하고 긍정/중립/부정/무응답으로 나뉜 결과값을 
# 3 ~ 0 사이의 값으로 mapping 후 return
# Naver CLOVA Sentiment Analysis api 활용
def SA():
    # global 변수 호출
    global textpath
    
    # 텍스트 파일 내용을 부른 후 저장
    f = open(textpath, 'r')
    text = f.readlines()
    f.close()
    
    # 만약, 어떤 텍스트도 입력되지 않았다면 무응답(0)으로 처리 후 return
    if not text:
        result = 0
        return result
    
    # 텍스트를 배열에서 문자열로 변환
    content = str(text)
    
    # 딕셔너리 생성 후 가독성 및 정렬을 위한 dumping 실시
    data = {"content": content}    
    json.dumps(data, indent=4, sort_keys=True)
    # Naver CLOVA Sentiment Analysis api 실행(response) 및 상태 메시지(rescode) 생성
    response = requests.post(url, data=json.dumps(data), headers=headers)
    rescode = response.status_code
    
    # 만약 api 실행이 성공적이라면(rescode == 200) 다음의 코드들을 실행
    if(rescode == 200):
        # 텍스트의 주된 sentiment 문자열을 추출
        idx = response.text.find('"sentiment":"')
        startIdx = idx + len('"sentiment":"')
        idx = response.text.find('","confidence')
        endIdx = idx        
        sentiment = response.text[startIdx:endIdx]
        
        # sentimenet 값(긍정/중립/부정)에 따라 result 값을 3 ~ 1로 mapping 후 return
        if sentiment == "positive":
            result = 3
        elif sentiment == "neutral":
            result = 2
        elif sentiment == "negative":
            result = 1

        return result

#4. function 'ask()'


# 1) 놀이에 대한 아동의 감상을 5초 단위로 녹음 및 음성 파일로 저장
# 2) Speech-to-Text(STT) 실행
# 3) Sentiment Analysis(SA)를 통해 텍스트 감성 분석 실행 후 결과값을 speech_dict에 저장
def ask(speech_dict):
    # global 변수 호출
    global audiopath
    
    # 완료된 STT 문장들을 저장할 string
    STT_sentence = ""
    
    # 질문에 대한 모든 대답을 저장할 텍스트 파일 생성
    # 각 질문에 대한 넘버링 작성
    f = open(answerpath, 'a')
    f.writelines(str(speech_dict["q_num"]) + ",")
    f.close()
    
    # 무응답이 나오기 전까지 계속 녹음 및 STT 실행
    cond = True
    while cond:
        cond = False
        # 음성 녹음
        record()
        
        # 녹음된 음성 파일 및 rate 불러오기
        y, sr = librosa.load(audiopath, sr=16000)

        period = y[sr*0 : sr*5]
        sf.write("./resample.wav", period, sr, 'PCM_16')
        
        # 5초 단위로 resample 된 음성 파일에 대해 STT() 실행
        # ValueError(무응답) 시 break
        try: 
            STT_sentence += STT()
        except ValueError:
            pass
    
    # 모든 대답에 대한 텍스트 파일(answerpath) 호출
    # 대답에 대한 STT를 마쳤다는 뜻에서 "온점(.)띄어쓰기('\n')" 작성
    f = open(answerpath, 'a')
    f.writelines(".\n")
    f.close()
    
    # STT 후 저장된 텍스트 파일에 대해 감성 분석을 실시 후 mapping된 값을 speech_dict 딕셔너리에 저장
    speech_dict['reply_score'] = SA()
    speech_dict['answers'] = STT_sentence

#5. function 'reply()'
class BreakToken:
    def __init__(self):
        self.is_cancelled = False
    
    def cancel(self):
        self.is_cancelled = True

# global 변수 text / audio / answer path에 각각 이름 부여,
# 멀티 쓰레딩으로 voice recognition과 eye tracking을 실행
def reply(cap, q_num, filename, answername):
    
    # parameter로 전달된 filename을 global 변수명으로 변경 후 저장
    global textpath, audiopath, answerpath
    global speech_dict, eye_gaze_dict
    global total_reply, total_eye_gaze

    speech_dict["q_num"] = q_num
    eye_gaze_dict["q_num"] = q_num
    
    textpath = filename + ".txt"
    audiopath = filename + ".wav"
    answerpath = str(answername) + ".txt"
    
    # 동일한 이름의 텍스트 파일 생성 방지 위해 path 초기화
    with open(textpath, "w") as f:
        pass
    
    cap = cap
    
    breakToken = BreakToken()
        
    # thread 정의
    # vr_thread: ask() 함수에 args 전달
    # et_thread: is_engagement() 함수에 args 전달
    sr_thread = threading.Thread(target=ask, args=(speech_dict, ))
    eg_thread = threading.Thread(target=eg.is_engagement, args=(cap, eye_gaze_dict, breakToken))
    
    # thread 실행
    sr_thread.start()
    eg_thread.start()
    
    # thread 종료
    sr_thread.join()
    breakToken.cancel()
    eg_thread.join()
    
    # 다 쓴 파일들 삭제
    os.remove(textpath)         # 임시 텍스트 파일 삭제
    os.remove("./resample.wav") # 임시 오디오 파일 삭제
    
    # 디버깅
    print("speech_dict:", speech_dict)
    print("eye_gaze_dict:", eye_gaze_dict)

    total_reply.append(list(speech_dict.values()))
    total_eye_gaze.append(list(eye_gaze_dict.values()))
    
def get_reply_list():
    global total_reply
    return total_reply

def get_eye_gaze_list():
    global total_eye_gaze
    return total_eye_gaze

#6. function 'normalization()'
# reply() 함수를 통해 구한 점수에 대한 정규화 실시
def calculate_score(scorelist, normalize=1):
    total = 0
    
    for i in range(len(scorelist)):
        total += scorelist[i][1]

    # ** change max reply score 4 -> 3
    norm_score = (total / float(3 * len(scorelist))) * normalize
    
    return norm_score