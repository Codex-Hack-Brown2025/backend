from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv()

import os
import requests
import json

class DifyTranslationResponse(BaseModel):
	translation: str
	moderation_status: int
	moderation_rationale: str

class DifyHandler:

	def __init__(self, user_name: str = "undefined", logger = None):
		self.user_name = user_name
		self.logger = logger
		self.dify_endpoint = "https://api.dify.ai/v1"

	def _parse_dify_response(self, raw_response: str) -> DifyTranslationResponse:
		parts = raw_response.split("&!&!&!&!&!")
		assert len(parts) == 3, f"Invalid response from Dify API: {raw_response}"

		return DifyTranslationResponse(
			translation=parts[0].strip(),
			moderation_status=int(parts[1].strip()),
			moderation_rationale=parts[2].strip())

	def _call_dify_translate(self, text: str, target_language: str, response_mode: str = "blocking"):
		headers = {
			"Authorization": f"Bearer {os.environ['DIFY_API_KEY']}",
			"Content-Type": "application/json"
		}

		payload = {
			"inputs": {
				"text": text,
				"target_language": target_language
			},
			"query": "f",
			"response_mode": response_mode,
			"conversation_id": "",
			"user": self.user_name,
		}

		r = requests.post(
			self.dify_endpoint + "/chat-messages",
			headers = headers,
			data = json.dumps(payload))
		
		result = r.json()

		if self.logger:
			self.logger.info(str(result))

		return result["answer"]
	
	def translate_text(self, original_text: str, target_language: str) -> DifyTranslationResponse:
		return self._parse_dify_response(self._call_dify_translate(original_text, target_language))
		
if __name__ == "__main__":
	handler = DifyHandler()
	print(handler.translate_text("hello world", "chinese"))
