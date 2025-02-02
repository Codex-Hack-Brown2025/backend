from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dify import DifyHandler
import uuid6
import logging

from mongodb import MongoHandler

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

def compare_comments(landmark_id_to_comments: dict[str, str], current_language: str, mongodb_handler: MongoHandler, dify_handler: DifyHandler) -> dict[str, tuple[str, str]]:
    """
    Compares the given comments with the mongodb-store comments.

    For new landmarks, create new instance with new landmark ids.

    For old landmarks, check if comment is different from mongodb comments.
    if different, create new instance with same landmark and new uuid.
    if same, return same landmark id.
    """

    translated_landmarks = dict()

    for landmark_id, comment in landmark_id_to_comments.items():
        landmark, uuid = landmark_id.split("@")

        if uuid == "NEW":
            # Is new landmark
            new_landmark_id = f"{landmark}@{uuid6.uuid8().hex}"
            mongodb_handler.store_landmark(new_landmark_id, current_language, comment)
            translated_landmarks[landmark_id] = (new_landmark_id, comment)
        else:
            # Not a new landmark
            result = mongodb_handler.get_translations(landmark_id)

            if result[current_language].strip() != comment:
                # Comment is edited
                new_landmark_id = f"{landmark}@{uuid6.uuid8().hex}"
                mongodb_handler.store_landmark(new_landmark_id, current_language, comment)
                translated_landmarks[landmark_id] = (new_landmark_id, comment)
            else:
                translated_landmarks[landmark_id] = (landmark_id, result[current_language])

    return translated_landmarks

def translate_comments(landmark_ids: list[str], target_language: str, mongodb_handler: MongoHandler, dify_handler: DifyHandler) -> dict[str, str]:
    """
    Translates landmarks, for each landmark, returns translation in target language
    """
    translated_landmarks = dict()

    for landmark_id in landmark_ids:
        # Check if the translation already exists in MongoDB 
        result = mongodb_handler.get_translations(landmark_id)

        translations = result["translations"]
        original_language = result["original_language"]

        if target_language not in translations:
            # If not, call the Dify API
            new_translation = dify_handler.translate_text(translations[original_language], target_language)
            # Store the translation in MongoDB (handled by your teammate)
            mongodb_handler.store_translation(landmark_id, target_language, new_translation)
            translated_landmarks[landmark_id] = new_translation
        else:
            translated_landmarks[landmark_id] = translations[target_language]

    return translated_landmarks

# Root endpoint
@app.get("/", summary="Root endpoint", description="Returns a welcome message.")
def read_root():
    return {"message": "Hello, World!"}


# Pydantic model for pull translation request
class PullTranslationRequest(BaseModel):

    # Note: Landmark ID is different from landmark because the ID is specific per branch/commit ID as well
    landmark_ids: list[str]
    target_language: str

# Translation endpoint
@app.post("/get_translations", summary="Gets translated landmarks", description="Translates comments in the code.")
async def get_translations(request: PullTranslationRequest): 
    logger.info(f"Translating to {request.target_language}")
    try:
        with MongoHandler() as mongodb_handler, DifyHandler() as dify_handler:
            result = translate_comments(request.landmark_ids, request.target_language, mongodb_handler, dify_handler)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(status_code=400, detail="Translation failed")

# Pydantic model for push translation request
class PushTranslationRequest(BaseModel):

    # Note: Landmark ID is different from landmark because the ID is specific per branch/commit ID as well
    landmark_id_to_comments: dict[str, str]
    current_language: str

@app.post("/update_translations")
async def update_translations(request: PushTranslationRequest):
    try:
        with MongoHandler() as mongodb_handler, DifyHandler() as dify_handler:
            result = compare_comments(request.landmark_id_to_comments, request.current_language, mongodb_handler, dify_handler)
        return JSONResponse(content=result)
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