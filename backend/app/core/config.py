import json
from typing import Any

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    DATABASE_URL: str = "sqlite:///./agri_ai.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CLAUDE_API_KEY: str = ""
    AI_PROVIDER: str = "claude"
    AI_API_KEY: str = ""
    AI_MODEL_NAME: str = "claude-3-5-sonnet-latest"
    AI_TIMEOUT_SECONDS: float = 45.0
    EXTERNAL_CONNECT_TIMEOUT_SECONDS: float = 5.0
    EXTERNAL_READ_TIMEOUT_SECONDS: float = 15.0
    EXTERNAL_WRITE_TIMEOUT_SECONDS: float = 10.0
    EXTERNAL_POOL_TIMEOUT_SECONDS: float = 5.0
    EXTERNAL_TOTAL_TIMEOUT_SECONDS: float = 20.0
    EXTERNAL_RETRY_COUNT: int = 2
    EXTERNAL_BACKOFF_SECONDS: float = 0.4
    WEATHER_API_KEY: str = ""
    WEATHER_PROVIDER: str = "open-meteo"
    WEATHER_API_BASE_URL: str = ""
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com"
    WEATHER_CACHE_TTL_SECONDS: int = 1800
    WEATHER_TIMEOUT_SECONDS: float = 20.0
    WEATHER_CONNECT_TIMEOUT_SECONDS: float = 5.0
    WEATHER_READ_TIMEOUT_SECONDS: float = 12.0
    WEATHER_RETRY_COUNT: int = 2
    REGION_COORDINATES_JSON: str = json.dumps(
        {
            "Ha Noi": {"latitude": 21.0285, "longitude": 105.8542},
            "TP.HCM": {"latitude": 10.8231, "longitude": 106.6297},
            "Da Nang": {"latitude": 16.0544, "longitude": 108.2022},
            "Can Tho": {"latitude": 10.0452, "longitude": 105.7469},
            "Lam Dong": {"latitude": 11.9404, "longitude": 108.4583},
            "Hai Phong": {"latitude": 20.8449, "longitude": 106.6881},
        }
    )

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = ""
    ZALO_OA_TOKEN: str = ""
    ZALO_OA_ID: str = ""
    ZALO_APP_ID: str = ""
    ZALO_APP_SECRET: str = ""
    ZALO_API_BASE_URL: str = "https://openapi.zalo.me"
    ESMS_API_KEY: str = ""
    ESMS_SECRET_KEY: str = ""
    ESMS_BRAND_NAME: str = "AgriAI"
    ESMS_SMS_TYPE: int = 2
    PRICE_SOURCE_URLS_JSON: str = json.dumps(
        [
            {"name": "agro.gov.vn", "url": "https://agro.gov.vn/index.aspx"},
            {"name": "agro.gov.vn-gia", "url": "https://agro.gov.vn/vn/nguonwmy.aspx"},
        ]
    )
    ENABLE_STOOQ_PRICE_SOURCE: bool = True
    EXCHANGE_RATE_API_URL: str = "https://open.er-api.com/v6/latest/USD"
    MARKET_API_BASE_URL: str = ""
    TAVILY_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    USD_VND_FALLBACK_RATE: float = 26000.0
    MARKET_NEWS_RSS_URLS_JSON: str = json.dumps(
        [
            "https://vnexpress.net/rss/kinh-doanh.rss",
            "https://vnexpress.net/rss/tin-moi-nhat.rss",
        ]
    )
    MARKET_NEWS_CACHE_TTL_SECONDS: int = 1800

    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    ENVIRONMENT: str = "development"
    UPLOAD_DIR: str = "storage/uploads"

    YOLO_MODEL_PATH: str = "ai_models/weights/best.pt"
    PRICE_MODEL_PATH: str = "ai_models/price_forecast/saved_models"
    HARVEST_MODEL_PATH: str = "ai_models/harvest_forecast/saved_models"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                return json.loads(stripped)
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def validate_production_secret(self):
        unsafe_keys = {"", "change-this-secret-key", "your-secret-key-change-this-in-production"}
        if self.ENVIRONMENT.lower() == "production" and self.SECRET_KEY in unsafe_keys:
            raise ValueError("SECRET_KEY must be set to a strong value in production")
        return self


settings = Settings()
