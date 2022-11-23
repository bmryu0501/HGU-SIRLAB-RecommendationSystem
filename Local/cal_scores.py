from FER import ferFunc as fer
from SpeechRecognition import srFunc as sr
from EyeGaze import eyegazeFunc as eyegaze
import makeCSV as mcsv

def calculate_total_score(test_num, UID, categoryID, taskID, total_reply, total_eye_gaze, total_emotion_dict, reply_w=0.58, eg_w=0.20, fer_w=0.22):
    ### reply
    total_reply_score = sr.calculate_score(total_reply, normalize=100)
    
    # make csv file for reply
    reply_csv_name = test_num + "reply.csv"
    reply_columns = ['QuestionNo', 'SA', 'Answers'] # ** change column name "SpeechScore" -> "ReplyScore"
    mcsv.makeCSV(UID, categoryID, taskID, reply_csv_name, total_reply, reply_columns)
    
    ### eye tracking
    # ** calculate eye_gaze_score
    total_eyegaze_score = eyegaze.calculate_score(total_eye_gaze, normalize=100)

    # make csv file for eye gaze
    eye_gaze_csv_name = test_num + "eye_gaze.csv"
    eye_gaze_columns = ['QuestionNo', 'EyeGazeFrame', 'TotalFrame', 'EyeGazeScore'] # ** add 'EyeGazeScore' column
    mcsv.makeCSV(UID, categoryID, taskID, eye_gaze_csv_name, total_eye_gaze, eye_gaze_columns)

    ### emotion 
    if total_emotion_dict != {}:
        # calculate score
        total_emotion_score = fer.calculate_score(normalize=100)
        # make csv file
        emotion_csv_name = test_num + "emotion.csv"
        emotion_columns = ['EmotionalState', 'Emotion']
        emotion_values = [[k, v] for k, v in total_emotion_dict.items()]
        mcsv.makeCSV(UID, categoryID, taskID, emotion_csv_name, emotion_values, emotion_columns)
    else:
        total_emotion_score = 0

    if total_emotion_score < 0:
        total_emotion_score = 0
        
    ### total engagement score
    engagement_score = reply_w * total_reply_score + eg_w * total_eyegaze_score + fer_w * total_emotion_score

    return total_reply_score, total_eyegaze_score, total_emotion_score, engagement_score
