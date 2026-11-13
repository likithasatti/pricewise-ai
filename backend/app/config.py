import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "PriceWise AI"
    PORT: int = 8080
    HOST: str = "0.0.0.0"

    # CORS
    CORS_ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

    # Database
    DATABASE_PATH: str = "pricewise.db"

    # Firebase / Firestore
    FIREBASE_PROJECT_ID: str = "pricewise-ai-be26e"
    FIREBASE_CLIENT_EMAIL: str = ""
    FIREBASE_PRIVATE_KEY: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str = ""

    # Amazon RapidAPI Provider
    RAPIDAPI_KEY: str = ""
    RAPIDAPI_HOST: str = "real-time-amazon-data.p.rapidapi.com"
    AMAZON_COUNTRY: str = "IN"
    AMAZON_TIMEOUT_SECONDS: int = 6

    # Flipkart Provider (ReefAPI or RapidAPI)
    REEFAPI_KEY: str = ""
    FLIPKART_API_KEY: str = ""
    FLIPKART_API_HOST: str = "real-time-flipkart-data2.p.rapidapi.com"
    REEFAPI_FLIPKART_URL: str = "https://api.reefapi.com/flipkart/v1/search"
    FLIPKART_TIMEOUT_SECONDS: int = 8

    # Price Tracking Scheduler
    TRACKING_INTERVAL_MS: int = 60000
    TRACKING_ENABLED: bool = True

    # AI Key (Gemini, OpenAI, or HuggingFace)
    AI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Mail configuration (for price drop alerts)
    MAIL_HOST: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""


settings = Settings()
