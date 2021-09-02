import pandas as pd
import os
import warnings
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from keras.models import load_model
from keras.layers import Input, Embedding, Flatten, Dense, Concatenate
from keras.models import Model
import numpy as np
warnings.filterwarnings('ignore')
index="dataset/data_recommended_system.csv"
path_model ="model/model.h5"


try:

  model = load_model(path_model)
except:
    print("no model fount")  

def process_model():
    dataset = pd.read_csv(index)
    train = dataset
    n_items=int(dataset['item_id'].max()+1)
    n_users=int(dataset['user_id'].max()+1)
    n_license=int(dataset['user_license'].max()+5)

    # creating book embedding path
    item_input = Input(shape=[1], name="Item-Input")
    item_embedding = Embedding(n_items+1, 5, name="Item-Embedding")(item_input)
    item_vec = Flatten(name="Flatten-Books")(item_embedding)

    # creating user embedding path
    user_input = Input(shape=[1], name="User-Input")
    user_embedding = Embedding(n_users+1, 5, name="User-Embedding")(user_input)
    user_vec = Flatten(name="Flatten-Users")(user_embedding)

    # creating license embedding path
    license_input = Input(shape=[1], name="License-Input")
    license_embedding = Embedding(n_license+1, 5, name="License-Embedding")(license_input)
    license_vec = Flatten(name="Flatten-Licenses")(license_embedding)

    # concatenate features
    conc = Concatenate()([item_vec, user_vec,license_vec])
    # add fully-connected-layers
    fc1 = Dense(128, activation='relu')(conc)
    fc2 = Dense(32, activation='relu')(fc1)
    out = Dense(1)(fc2)
    # Create model and compile it
    model = Model([user_input, item_input,license_input], out)
    model.compile('adam', 'mean_squared_error')

    model.fit([train.user_id, train.item_id,train.user_license], train.progress, epochs=5, verbose=1)
    model.save(path_model)
    model = load_model(path_model)
    return


def predict(f):
    data = pd.read_csv(index)
    user_id =[]
    user_license=[]
    avail_product = data['item_id'].unique()
    for x in avail_product:
      user_id.append(f.user_id)
      user_license.append(f.user_license)
    vv = pd.DataFrame({'user_id': user_id,
                   'item_id': avail_product,
                   'user_license': user_license})  
    predictions = model.predict([vv.user_id , vv.item_id , vv.user_license])
    result = []
    pred= predictions.tolist()
    for i in range(0,len(avail_product)):

      result.append({"item":int(vv.item_id.iloc[i]),"prog":pred[i][0]})
    result = sorted(result, key=lambda k: k['prog'])[::-1][:10] 
    return {"most_item":result}



def add_new_data(f):
    try:
      data = pd.read_csv(index)
    except:
      data = pd.DataFrame({'user_id': [],
                   'item_id': [],
                   'user_license': [],
                    'current_level': [],
                    'total_level': []})

    new_row = {'user_id': f.user_id,
                   'item_id': f.item_id,
                   'user_license': f.user_license,
                    'current_level': f.current_level,
                     'total_level': f.total_level}


    data = data.append(new_row, ignore_index = True)  
    data=data.groupby(["user_id","user_license","item_id"]).agg({'current_level':['max'],'total_level':['max']}).reset_index()

    data.columns = ['user_id', 'user_license', 'item_id','current_level','total_level']

    data['progress'] = data.apply(lambda x: x.current_level/x.total_level, axis=1)

    data.to_csv(index,index=False)             

    return {"result":"success add"}


def clear_dataset():
  data = pd.DataFrame({'user_id': [],
                   'item_id': [],
                   'user_license': [],
                    'current_level': [],
                    'total_level': []})
  data.to_csv(index,index=False)
  return


