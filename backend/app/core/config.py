from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database - SQL Server
    # SQL Server Authentication with sa user
    DATABASE_URL: str = "mssql+pyodbc://sa:123@localhost\\\\SQLEXPRESS02/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Keys
    CLAUDE_API_KEY: str = ""
    WEATHER_API_KEY: str = ""
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # AI Models
    YOLO_MODEL_PATH: str = "ai_models/weights/best.pt"
    PRICE_MODEL_PATH: str = "ai_models/price_forecast/saved_models"
    HARVEST_MODEL_PATH: str = "ai_models/harvest_forecast/saved_models"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
