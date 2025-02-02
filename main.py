import base64
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from dify import DifyHandler
import uuid6
import logging
import requests
import os
import json

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

def compare_comments(landmark_id_to_comments: dict[str, str], current_language: str, mongodb_handler: MongoHandler, dify_handler: DifyHandler) -> dict[str, dict[str, str]]:
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
            translated_landmarks[landmark] = {
                    "landmark_id": new_landmark_id,
                    "comment": comment
                }
        else:
            # Not a new landmark
            result = mongodb_handler.get_translations(landmark_id)

            if result["translations"][current_language].rstrip() != comment:
                # Comment is edited
                new_landmark_id = f"{landmark}@{uuid6.uuid8().hex}"
                mongodb_handler.store_landmark(new_landmark_id, current_language, comment)
                translated_landmarks[landmark] = {
                    "landmark_id": new_landmark_id,
                    "comment": comment
                }
            else:
                translated_landmarks[landmark] = {
                    "landmark_id": landmark_id,
                    "comment": result["translations"][current_language]
                }

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
            mongodb_handler.store_translation(landmark_id, target_language, new_translation.translation)
            translated_landmarks[landmark_id] = new_translation.translation
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
        mongodb_handler = MongoHandler()
        dify_handler = DifyHandler()
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
        mongodb_handler = MongoHandler()
        dify_handler = DifyHandler()
        result = compare_comments(request.landmark_id_to_comments, request.current_language, mongodb_handler, dify_handler)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(status_code=400, detail="Translation failed")
    
class LanguagePreferenceRequest(BaseModel):
    user_name: str

@app.post("/get_user_preference")
async def get_user_language_preference(request: LanguagePreferenceRequest):
    try:
        mongodb_handler = MongoHandler()
        user_object = mongodb_handler.get_user(request.user_name)
        return JSONResponse(content={
            "language": user_object["language"]
        })
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail="Get User Preference failed")


@app.get("/github/{owner}/{repo}/{user_name}/content/{path:path}")
async def get_github_content(owner: str, repo: str, user_name: str, path: str = "", branch: str = "main"):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    try:
        mongodb_handler = MongoHandler()
        user_object = mongodb_handler.get_user(user_name)
        response = requests.get(
            url,
            params={"ref": branch},
            headers={
                "Authorization": f"Bearer {user_object['PAT']}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="GitHub API error")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class UserCreationRequest(BaseModel):
    user_name: str
    language: str
    pat: str

@app.post("/create/user")
async def create_user(request: UserCreationRequest):
    try:
        mongodb_handler = MongoHandler()
        mongodb_handler.create_user(request.user_name, request.language, request.pat)
        return JSONResponse(content={"result": "success"}, status_code=200)
    except:
        raise HTTPException(status_code=400, detail="User creation failed")
    
@app.get("/exists/user/{user_name}")
async def exists_user(user_name: str):
    try:
        mongodb_handler = MongoHandler()
        res = mongodb_handler.get_user(user_name)
        return JSONResponse(content={"result": ("exists" if res is not None else "does not exist")}, status_code=200)
    except:
        raise HTTPException(status_code=400, detail="User creation failed")
    

@app.post("/github/{owner}/{repo}/{user_name}/initialize")
async def initialize_repo(owner: str, repo: str, user_name: str):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees"

    try:
        mongodb_handler = MongoHandler()
        user_object = mongodb_handler.get_user(user_name)
        headers = {
            "Authorization": f"token {user_object['PAT']}",
            "Accept": "application/vnd.github.v3+json",
        }

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/comment_files/empty.py"

        data = {
            "message": "Create comment_files/ directory",
            "content": base64.b64encode("# this is initially left blank".encode()).decode(),
            "branch": "main",
        }

        r = requests.put(
            url,
            headers=headers,
            data=json.dumps(data)
        )

        if r.status_code != 201:
            print(r.text)
            raise HTTPException(status_code=r.status_code, detail="GitHub API error")
        
        with open("./setup_hooks.sh", "r") as file_obj:
            content = "\n".join(file_obj.readlines())

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/setup_hooks.sh"

        data = {
            "message": "Create setup_hooks.sh",
            "content": base64.b64encode(content.encode()).decode(),
            "branch": "main",
        }
        r = requests.put(
            url,
            headers=headers,
            data=json.dumps(data)
        )

        if r.status_code != 201:
            print(r.text)
            raise HTTPException(status_code=r.status_code, detail="GitHub API error")

        folder_path = "scripts/hooks/"
        for f in os.listdir(folder_path):
            filepath = os.path.join(folder_path, f)
            with open(filepath, "r") as file_obj:
                content = "\n".join(file_obj.readlines())
            fp = os.path.join(folder_path, f)
            data = {
                "message": f"Create {fp}",
                "content": base64.b64encode(content.encode()).decode(),
                "branch": "main",
            }
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{fp}"
            r = requests.put(
                url,
                headers=headers,
                data=json.dumps(data)
            )

            if r.status_code != 201:
                print(r.text)
                raise HTTPException(status_code=r.status_code, detail="GitHub API error")
        return JSONResponse(content = {"result": "success"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
 uvicorn.run("main:app", host="0.0.0.0", port=8000)

# read repos
# read/write content