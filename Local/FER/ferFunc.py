import torch
from torchvision import transforms
from collections import Counter
import threading
import cv2 as cv

#부모의 부모 디렉토리에서 main을 실행할 경우를 위해 부모 디렉토리 삽입
#from Facial_Expression_Recognition.model import cnn
#from Facial_Expression_Recognition.preprocess import preprocess
from FER.model import cnn
import FER.preprocess as preprocess

#classes = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
classes = ['frown', 'happy', 'neutral', 'surprise']

#global state_time, state_num, state_emotion_list, emotion_dict
global model, model_path, model_name
model_path = "./FER/pretrained/"
model_name = "pretrained_reduced_refined_fer_cnn3.pt"

state_time = 5
state_num = 0
state_emotion_list = []
emotion_dict = {}    
play_end = False

### fer main
'''
timer
'''
def start_timer():
    global state_num, state_emotion_list, emotion_dict, play_end

    if state_emotion_list != []:
        most_common_emotion = decide_emotion()
        
        # 대부분의 frame에서 얼굴이 인식되지 않거나 전처리가 되지 않는 경우는 emotion state를 카운트하지 않는다
        if most_common_emotion != 'NotDefined':
            emotion_dict[state_num] = most_common_emotion
            # print(emotion_dict)

            state_emotion_list = []
            state_num += 1

    timer = threading.Timer(5, start_timer)
    timer.setDaemon(True)
    timer.start()
    
    if play_end == True:
        timer.cancel()

'''
end timer
'''
def end_timer():
    global play_end
    play_end = True

    
'''
facial expression recognition
'''
def fer_process(frame):
    global classes

    result = preprocess.reduced_face_mesh(frame) # for showing the real-time video
    
    if result is None:
        return
    
    preprocess_frame = preprocess.image_preprocessing(frame) # input for cnn
    
    # if cannot preprocess image (difficulty of extracting roi or marking landmark...)
    if preprocess_frame is None:
        state_emotion_list.append("NotDefined")
        text =  "Not Defined."
        print("cannot preprocess")
    # if success to preprocess image
    else:
        input_tensor = array2tesnor(preprocess_frame)
        output, top_p, top_class = classify_emotion(input_tensor)

        state_emotion_list.append(classes[top_class])
        # to write on the frame
        text = classes[top_class]
        result = print_label(result, output, text) # feedback

    # put final class on the frame
    cv.putText(result, text, (50, 100), cv.FONT_ITALIC, 5, (0,0,255), 5)
    # print(text)
    return result

### about classify emotion
'''
initialize CNN model and load pretrained model
'''
def model_init():
    global model, model_name, model_path
    # load pretrained model
    #model_name = "pretrained_reduced_refined_fer_cnn.pt"
    #path = './Facial_Expression_Recognition/model/'
    
    model = cnn.CNN(num_classes=4)
    model.load_state_dict(torch.load(model_path+model_name, map_location=torch.device('cpu')))
    model.eval()

    return 

'''
classify emotion by using CNN model.
and return output, top class index, top class probability
'''
def classify_emotion(tensor):
    global model

    # classify facial expression
    output = model.forward(tensor)
    ps = torch.exp(output)

    prob = torch.nn.functional.softmax(output, dim=1)
    top_p, top_class = prob.topk(1, dim=1) # extract top class index and probability

    return output, top_p, top_class

'''
change array to tensor for CNN input
'''
def array2tesnor(image):
    # transform for image
    trans = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])
    tensor_image = trans(image).unsqueeze(dim=0)

    return tensor_image

'''
apply logic for deciding emotion
'''
def decide_emotion():
    global state_emotion_list

    # emotion list의 최빈값
    most = Counter(state_emotion_list).most_common(1)
    detected = most[0][0]

    # 만약 emotion list의 최빈값이 neutral이지만 neutral 이외에 또 다른 감정이 detect 되었을 때
    if detected == 'neutral' and len(Counter(state_emotion_list)) > 2:
        if Counter(state_emotion_list).most_common()[1][1] >= 2:
            detected = Counter(state_emotion_list).most_common()[1][0]
    
    return detected

### about printing on the image
'''
print another label on the image if there are other labels with a high probability except top_class
'''
def print_label(frame, output, top_class):
    global classes
    # feedback
    count = 2
    for i in range(len(classes)):
        if output[0][i] > 0.5 and classes[i] != top_class:
            x = 100 * count
            string = str(classes[i]) + ':' + str(output[0][i])
            cv.putText(frame, string, (100, x), cv.FONT_ITALIC, 3, (0,0,0), 5)
            count += 1
    return frame

def fer_thread(cap):
    model_init()
    start_timer()
    
    cap = cap
    
    while cap.isOpened():
        success, frame = cap.read()
        
        if not success:
            print("Ignoring empty camera frame.")
            continue
        
        result = fer_process(frame)
        
        # if result is None:
        #     cv.imshow("Video", frame)
        # else:
        #     cv.imshow("Video", result)
        
        if cv.waitKey(5) & 0xFF == 27:
            break
        else:
            continue
        
    end_timer()

### about calculating emotion score
'''
calculate emotional engagement score and return it.
'''
def calculate_score(normalize=1):
    global emotion_dict

    print("\ncalculate emotion score...")
    high = 2; middle = 1
    emotional_score = 0
    emotional_engagement_score = 0

    score = {'happy': high, 'neutral': high, 'surprise': high, 'frown': middle}
    emotions_count = Counter(list(emotion_dict.values())).most_common()
    print(emotions_count)

    for emotion, count in emotions_count:
        emotional_score += score[emotion] * count
    print("total emotional score:", emotional_score)
    emotional_engagement_score = (emotional_score / (2 * len(emotion_dict))) * normalize

    return emotional_engagement_score

def get_emotion_dict():
    global emotion_dict
    return emotion_dict