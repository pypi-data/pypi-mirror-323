import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BACKEND_URL: str = "https://autodocify-backend.onrender.com/"

    class Config:
        env_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "env_files", ".env"
        )

        env_file_encoding = "utf-8"


settings = Settings()
