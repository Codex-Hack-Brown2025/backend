from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class TranslationRequest(BaseModel):
    text: str
    target_language: str

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/translate")
def translate_comment(request: TranslationRequest):
    if request.target_language == "es":
        return {"translation": f"Translated to Spanish: {request.text}"}
    elif request.target_language == "fr":
        return {"translation": f"Translated to French: {request.text}"}
    else:
        raise HTTPException(status_code=400, detail="Unsupported language")