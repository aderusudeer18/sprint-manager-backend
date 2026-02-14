import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Sprint Manager API"
    PROJECT_VERSION: str = "1.0.0"

    # Database
    POSTGRES_URL: str = os.getenv("POSTGRES_URL")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super_secret_key_change_me_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Typically 15-60 mins for access tokens

settings = Settings()
