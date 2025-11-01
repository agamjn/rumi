"""
Configuration management for Rumi.

Loads settings from environment variables with type validation.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None

    # Anthropic
    anthropic_api_key: Optional[str] = None

    # Bedrock Knowledge Base
    bedrock_kb_id: Optional[str] = None
    bedrock_data_source_id: Optional[str] = None

    # DynamoDB
    dynamodb_state_table: str = "rumi_state"

    # Letta
    letta_base_url: str = "http://localhost:8080"

    # Environment
    environment: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
