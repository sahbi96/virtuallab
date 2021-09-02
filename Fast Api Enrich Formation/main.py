from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from extract import Enrich_Formation as extr
from extract import Translate_Text as tr
from pydantic import BaseModel

class Foramtion(BaseModel):
    name: str
    short_description :str
    full_description :str

class Trans(BaseModel):
    text: str 


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
    


@app.post("/trans/")
async def translate(data:Trans):
    try:
       result = tr(data.text)
    except:
        return JSONResponse(status_code=400, content={"message": "format des données incompatibles"})
        
    return result


@app.post("/enrich/")
async def extract(data:Foramtion):
    try:
       result = extr(data)
    except:
        return JSONResponse(status_code=400, content={"message": "format des données incompatibles"})
        
    return result

