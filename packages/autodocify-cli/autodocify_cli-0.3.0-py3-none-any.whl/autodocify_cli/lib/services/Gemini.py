import google.generativeai as genai
import requests
from autodocify_cli.core.settings.config import settings


class GeminiService:
    def __init__(self, prompt):
        self.prompt = prompt
        self.url = settings.BACKEND_URL
        self.data = {"prompt": prompt}

    def run(self) -> None:
        response = requests.post(url=f"{self.url}/api/gemini", json=self.data)
        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(
                "An Error Occured. Please Send A Message To The Support Team If This Persists."
            )
