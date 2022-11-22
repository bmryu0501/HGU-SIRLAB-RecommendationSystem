import pandas as pd
import os

# ** set the csv name and columns
achievement_csv_name = 'achivement.csv'
achievement_csv_columns = ['ParentScore', 'ExpertScore', 'AchievedScore', 'NotAchievedScore']

engagement_csv_name = 'engagement.csv'
engagement_csv_columns = ['EmotionScore', 'ReplyScore', 'EyeGazeScore', 'EngagementScore'] # ** 추후에 'EngaegmentLevel' 추가

def list2df(lst, cols):
    if isinstance(lst[0], list):
        df = pd.DataFrame(lst, columns=cols)
    else:
        df = pd.DataFrame([lst], columns=cols)
        
    return df

# make new csv file
def makeCSV(uid, categoryID, taskID, csv_name, lst, cols):
    path = "./users/"
    os.makedirs(path, exist_ok=True)    
    path = path + uid
    os.makedirs(path, exist_ok=True)
    path = path + "/" + categoryID
    os.makedirs(path, exist_ok=True)
    path = path + "/" + taskID
    os.makedirs(path, exist_ok=True)
    
    df = list2df(lst, cols)
    
    df.to_csv(path+"/"+csv_name)

# ** add new column in csv file