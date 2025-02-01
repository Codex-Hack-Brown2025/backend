from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import logging

# Initialize FastAPI app
app = FastAPI(
    title="Local Translation Tool",
    description="A tool to translate comments locally and manage translations using MongoDB",
    version="1.0.0"
)

# Set up logging to track requests and responses
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DIFY API implementation (replace with actual API key and URL)
DIFY_API_KEY = "your-dify-api-key"
DIFY_API_URL = "https://api.dify.ai/v1/translate"

# Pydantic model for translation request
class TranslationRequest(BaseModel):
    code: str
    target_language: str


async def translate_comments(code: str, target_language: str, db) -> dict:
    """
    Translates comments in the code and returns the translated code.
    """
    comments = extract_comments(code)
    translated_code = code

    for comment in comments:
        # Check if the translation already exists in MongoDB 
        translation = db.get_translation(comment, target_language)  # Placeholder for MongoDB logic

        if not translation:
            # If not, call the Dify API
            translation = await call_dify_api(comment, target_language)
            # Store the translation in MongoDB (handled by your teammate)
            db.store_translation(comment, target_language, translation)  # Placeholder for MongoDB logic

        # Replace the comment with the translated version
        translated_code = translated_code.replace(comment, f"# {translation}")

    return {"translated_code": translated_code}

# Root endpoint
@app.get("/", summary="Root endpoint", description="Returns a welcome message.")
def read_root():
    return {"message": "Hello, World!"}

# Translation endpoint
@app.post("/translate", summary="Translate comments", description="Translates comments in the code.")
async def translate_code(request: TranslationRequest, db): 
    logger.info(f"Translating code to {request.target_language}")
    try:
        result = await translate_comments(request.code, request.target_language, db)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(status_code=400, detail="Translation failed")








































# class TranslationRequest(BaseModel):
#     text: str
#     target_language: str

# @app.get("/")
# def read_root():
#     return {"message": "Hello, World!"}

# @app.post("/translate")
# def translate_comment(request: TranslationRequest):
#     if request.target_language == "es":
#         return {"translation": f"Translated to Spanish: {request.text}"}
#     elif request.target_language == "fr":
#         return {"translation": f"Translated to French: {request.text}"}
#     else:
#         raise HTTPException(status_code=400, detail="Unsupported language")