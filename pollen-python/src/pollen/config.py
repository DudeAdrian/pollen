"""Configuration management for Pollen AI Agent"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Pollen configuration settings"""
    
    # Service
    POLLEN_AGENT_NAME: str = Field(default="pollen-agent-001")
    POLLEN_PORT: int = Field(default=9000)
    POLLEN_HOST: str = Field(default="0.0.0.0")
    POLLEN_ENV: str = Field(default="development")
    POLLEN_LOG_LEVEL: str = Field(default="info")
    
    # Hive
    HIVE_URL: str = Field(default="http://localhost:3000")
    HIVE_WS_URL: str = Field(default="ws://localhost:3000/ws/pollen")
    HIVE_API_KEY: str = Field(default="")
    HIVE_RECONNECT_INTERVAL: int = Field(default=5)
    HIVE_MAX_RECONNECT_ATTEMPTS: int = Field(default=10)
    
    # Sofie
    SOFIE_URL: str = Field(default="http://localhost:8000")
    SOFIE_WS_URL: str = Field(default="ws://localhost:8000/ws")
    SOFIE_MODEL: str = Field(default="llama3.1:70b")
    SOFIE_TIMEOUT: int = Field(default=30)
    
    # Terracare Ledger
    TERRACARE_RPC_URL: str = Field(default="http://localhost:8545")
    TERRACARE_CHAIN_ID: int = Field(default=1337)
    TERRACARE_CONTRACT_POLLEN: str = Field(default="")
    TERRACARE_CONTRACT_HONEY: str = Field(default="")
    DEPLOYER_PRIVATE_KEY: str = Field(default="")
    
    # Ollama
    OLLAMA_HOST: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL: str = Field(default="llama3.1:8b")
    OLLAMA_TIMEOUT: int = Field(default=60)
    
    # Encryption
    POLLEN_MASTER_KEY: str = Field(default="")
    POLLEN_FERNET_KEY: str = Field(default="")
    
    # Heartware
    HEARTWARE_URL: str = Field(default="http://localhost:3001")
    HEARTWARE_API_KEY: str = Field(default="")
    HEARTWARE_DEVICE_ID: str = Field(default="")
    HEARTWARE_POLL_INTERVAL: int = Field(default=60)
    
    # Social Media
    TWITTER_BEARER_TOKEN: str = Field(default="")
    TWITTER_API_KEY: str = Field(default="")
    TWITTER_API_SECRET: str = Field(default="")
    TWITTER_ACCESS_TOKEN: str = Field(default="")
    TWITTER_ACCESS_SECRET: str = Field(default="")
    INSTAGRAM_USERNAME: str = Field(default="")
    INSTAGRAM_PASSWORD: str = Field(default="")
    LINKEDIN_EMAIL: str = Field(default="")
    LINKEDIN_PASSWORD: str = Field(default="")
    
    # Content Creation
    SD_API_URL: str = Field(default="http://localhost:7860")
    SD_MODEL: str = Field(default="stable-diffusion-xl-base-1.0")
    FFMPEG_PATH: str = Field(default="/usr/bin/ffmpeg")
    VAULT_PATH: str = Field(default="./data/vault")
    QUEUE_PATH: str = Field(default="./data/queue")
    CACHE_PATH: str = Field(default="./data/cache")
    
    # Shadow Accumulator
    SHADOW_HONEY_THRESHOLD: int = Field(default=1000)
    GRADUATION_AUTO_ENABLED: bool = Field(default=False)
    SHADOW_DB_PATH: str = Field(default="./data/shadow.db")
    
    # Feature Flags
    ENABLE_WELLNESS_AGENT: bool = Field(default=True)
    ENABLE_CREATIVE_AGENT: bool = Field(default=True)
    ENABLE_SOCIAL_AGENT: bool = Field(default=True)
    ENABLE_TECHNICAL_AGENT: bool = Field(default=True)
    ENABLE_ADMIN_AGENT: bool = Field(default=True)
    AUTO_EXECUTE_TASKS: bool = Field(default=False)
    REQUIRE_CONSENT_FOR_PUBLISH: bool = Field(default=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
