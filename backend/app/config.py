import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "Smart Order Fulfillment and Delivery Promise Optimization System"
    APP_ENV: str = "development"
    API_PREFIX: str = "/api"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fulfillment.db")
    
    # Random Seed
    SEED: int = 20261022
    
    # Default Optimization Weights (Sum = 1.0)
    WEIGHT_INVENTORY: float = 0.30
    WEIGHT_SPEED: float = 0.25
    WEIGHT_CAPACITY: float = 0.15
    WEIGHT_COST: float = 0.15
    WEIGHT_RELIABILITY: float = 0.10
    WEIGHT_RISK: float = 0.05

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
