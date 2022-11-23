'''
This python file make dataset
'''

#%%imports
import pandas as pd
import numpy as np
import random
import math


#%% Dataset for achievement recommendation

path = '../dataset/'
num_data = 1000
num_user = 100
num_task = 40


frame_dict_achievement = {'UserID' : [], 'CategoryID' : [], 'TaskID' : [], 'Parent' : [], 'Expert': []}
df = pd.DataFrame(frame_dict_achievement)

for i in range(num_data):
    uid = random.randint(0, num_user-1)
    tid = random.randint(0, num_task-1)
    categoryid = math.floor(tid/num_task*4)
    
    if math.floor(uid/num_user*4) != math.floor(tid/num_task*4) :
        parent = random.randint(90, 100)
        expert = random.randint(90, 100)
    else:
        parent = random.randint(0, 10)
        expert = random.randint(0, 10)
    
    new_row = [uid, categoryid, tid, parent, expert]
    df.loc[len(df)] = new_row

df = df.sort_values(by=['UserID', 'CategoryID', 'TaskID', 'Parent', 'Expert'], axis=0)

df.to_csv(path + 'achievement.csv')

#%% dataset for Engagement

path = '../dataset/'
num_data = 1000
num_user = 100
num_task = 40

def get_engagement_level(engagement_score):
    if engagement_score < 30:
        return 0
    elif engagement_score < 60:
        return 50
    else:
        return 100

frame_dict_engagement = {'UserID' : [], 'CategoryID' : [], 'TaskID': [], 'Engagement Score' : [], 'Engagement Level' : []}
df_engagement = pd.DataFrame(frame_dict_engagement)

for i in range(num_data):
    uid = random.randint(0, num_user-1)
    tid = random.randint(0, num_task-1)
    categoryid = math.floor(tid/num_task*4)
    
    if math.floor(uid/num_user*4) == math.floor(tid/num_task*4) :
        engagement_score = random.randint(50, 100)
    else:
        engagement_score = random.randint(0, 40)
    engagement_level = get_engagement_level(engagement_score)

    new_row = [uid, categoryid, tid, engagement_score, engagement_level]
    df_engagement.loc[len(df_engagement)] = new_row
    
# uid = 100
# for tid in [1, 12, 25, 35, 2, 14, 26, 36]:
#     categoryid = int(math.floor(tid/num_task*4))
#     engagement_score = random.randint(0, 50) if categoryid < 3 else random.randint(50, 100)
#     engagement_level = get_engagement_level(engagement_score)
#     new_row = [uid, categoryid, tid, engagement_score, engagement_level]
#     df_engagement.loc[len(df_engagement)] = new_row

df_engagement.to_csv(path + 'engagement.csv', index=False)
# %%
