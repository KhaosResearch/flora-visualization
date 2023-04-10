from pathlib import Path

from pydantic import BaseSettings


class _Settings(BaseSettings):
    MONGO_URI: str = None

    MONGO_COLLECTION_FLORA: str = None
    MONGO_DB_FLORA: str = None

    MONGO_COLLECTION_GENOM: str = None
    MONGO_DB_GENOM: str = None

    MINIO_HOST: str = None
    
    MINIO_BUCKET_FLORA: str = None
    MINIO_ACCESS_KEY_FLORA: str = "minio"
    MINIO_SECRET_KEY_FLORA: str = "minio"



    class Config:
        env_file = ".env"
        file_path = Path(env_file)
        if not file_path.is_file():
            print("⚠️ `.env` not found in current directory")
            print("⚙️ Loading settings from environment")
        else:
            print(f"⚙️ Loading settings from dotenv @ {file_path.absolute()}")


settings = _Settings()
