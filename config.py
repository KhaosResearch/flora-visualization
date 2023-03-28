from pathlib import Path

from pydantic import BaseSettings


class _Settings(BaseSettings):
    PORT: int = None
    MONGO_URI: str = None
    MONGO_DATABASE: str = None
    MONGO_COLLECTION: str = None
    MINIO_HOST: str = None
    MINIO_BUCKET: str = None
    MINIO_ACCESS_KEY: str = "minio"
    MINIO_SECRET_KEY: str = "minio"


    class Config:
        env_file = ".env"
        file_path = Path(env_file)
        if not file_path.is_file():
            print("⚠️ `.env` not found in current directory")
            print("⚙️ Loading settings from environment")
        else:
            print(f"⚙️ Loading settings from dotenv @ {file_path.absolute()}")


settings = _Settings()
