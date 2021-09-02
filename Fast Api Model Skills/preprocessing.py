import pandas as pd
import os
import warnings
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans 
import numpy as np
warnings.filterwarnings('ignore')
index="dataset/data_skills.csv"
saved_data="dataset/data_skills_user.csv"




def process_model():
    dataset = pd.read_csv(index)
    dataset=dataset.groupby(["user_id"]).agg({'current_level':['mean'],'item_id':['count'],'total_level':['mean'],'timestamp':['mean'],'user_license':['mean']}).reset_index()
    dataset.columns = dataset.columns.get_level_values(0)
    dataset['progress'] = dataset.apply(lambda x: x.current_level/x.total_level, axis=1)  
    X = dataset.values[:,1:]
    X = np.nan_to_num(X)
    StandardScaler().fit_transform(X)
    clusterNum = 3
    k_means = KMeans(init = "k-means++", n_clusters = clusterNum, n_init = 12)
    k_means.fit(X)
    labels = k_means.labels_    
    saved_data_user = pd.DataFrame({'user_id': dataset['user_id'].values,'class': labels})
    saved_data_user.to_csv(saved_data,index=False)
    return


def predict(f):
    result = 0
    data_users = pd.read_csv(saved_data)
    vv = data_users.loc[data_users['user_id'] == f.user_id]
    if len(vv)>0:
      result = vv.iloc[0]['class']
    return {"user_class":result}



def add_new_data(f):
    try:
      data = pd.read_csv(index)
    except:
      data = pd.DataFrame({'user_id': [],
                   'item_id': [],
                   'user_license': [],
                    'current_level': [],
                    'timestamp':[],
                    'score':[],
                    'total_level': []})

    new_row = {'user_id': f.user_id,
                   'item_id': f.item_id,
                   'user_license': f.user_license,
                    'current_level': f.current_level,
                    'timestamp':f.timestamp,
                    'score':f.score,
                     'total_level': f.total_level}


    data = data.append(new_row, ignore_index = True)  
    data=data.groupby(["user_id","item_id"]).agg({'current_level':['max'],'total_level':['max'],'timestamp':['mean'],'user_license':['max']}).reset_index()
    data.columns = data.columns.get_level_values(0)   
    data['progress'] = data.apply(lambda x: x.current_level/x.total_level, axis=1)
    data.to_csv(index,index=False)        

    return {"result":"success add"}


def clear_dataset():
  data = pd.DataFrame({'user_id': [],
                   'item_id': [],
                   'user_license': [],
                    'current_level': [],
                    'timestamp':[],
                    'score':[],
                    'total_level': []})
  data.to_csv(index,index=False)
  return


