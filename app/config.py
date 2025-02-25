import os
from pydantic import BaseSettings, SecretStr

class Settings(BaseSettings):
    # Core settings
    PROJECT_NAME: str = "Blog API"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./prod.db")
    
    # Authentication settings
    SECRET_KEY: SecretStr = SecretStr(os.getenv("SECRET_KEY", "generate-a-secure-secret-key"))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # AWS settings
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: SecretStr = SecretStr(os.getenv("AWS_SECRET_ACCESS_KEY", ""))
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "blog-media-bucket")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
