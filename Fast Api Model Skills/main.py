from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from preprocessing  import add_new_data as add_new
from preprocessing  import process_model as proc_model
from preprocessing  import predict as pred
from preprocessing  import clear_dataset as clear
from pydantic import BaseModel

class New_Data(BaseModel):
    user_id:int
    item_id:int
    user_license:int
    current_level:int
    total_level:int
    score:float
    timestamp:float


class User_Data(BaseModel):
    user_id:int

  

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/clear_dataset/")
async def clear_dataset():
    try:
       result = clear()
    except:
        return JSONResponse(status_code=400, content={"message": "format des données incompatibles"})
        
    return result

@app.post("/predict_to_user/")
async def predict_to_user(data:User_Data):
    try:
       result = pred(data)
    except:
        return JSONResponse(status_code=400, content={"message": "format des données incompatibles"})
        
    return result



@app.post("/update_model/")
async def update_model():
    result = proc_model()
    # try:
    #    result = proc_model()
    # except:
    #     return JSONResponse(status_code=400, content={"message": "format des données incompatibles"})
        
    return result


@app.post("/add_new/")
async def add_data_new(data:New_Data):
    result = add_new(data)
    # try:
    #    result = add_new(data)
    # except:
    #     return JSONResponse(status_code=400, content={"message": "format des données incompatibles"})
        
    return result

