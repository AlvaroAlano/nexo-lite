from pydantic_settings import BaseSettings
from uuid import UUID


class Settings(BaseSettings):
    DATABASE_URL: str
    DEMO_USER_ID: UUID = UUID("00000000-0000-0000-0000-000000000001")
    FRONTEND_URL: str = "http://localhost:5173"
    SUPABASE_JWT_SECRET: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
