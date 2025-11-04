"""
Configuration management for Rumi.

Loads settings from environment variables with type validation.
Supports both AWS SSO and traditional access keys.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # AWS Configuration
    # For AWS SSO: Set AWS_PROFILE to your SSO profile name
    # For traditional keys: Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
    aws_region: str = "us-east-1"
    aws_profile: Optional[str] = None  # For AWS SSO
    aws_access_key_id: Optional[str] = None  # For traditional auth
    aws_secret_access_key: Optional[str] = None  # For traditional auth

    # AI Provider APIs (Task 2.3 - optional until then)
    anthropic_api_key: Optional[str] = None  # If using Claude
    openai_api_key: Optional[str] = None      # If using OpenAI

    # OpenAI Model Selection (for classification and other tasks)
    # Options: "gpt-4o-mini" (cheapest), "gpt-4o" (best), "gpt-4-turbo" (overkill)
    openai_model: str = "gpt-4o-mini"  # Default to cheapest, works great

    # Bedrock Knowledge Base (Task 3.1 - optional until then)
    bedrock_kb_id: Optional[str] = None
    bedrock_data_source_id: Optional[str] = None

    # DynamoDB (Task 1.1 - will create table then)
    dynamodb_state_table: str = "rumi_state"

    # Letta (Task 4.1 - optional until then)
    letta_base_url: str = "http://localhost:8080"

    # Fathom API (Task 6.1 - optional until then)
    fathom_api_key: Optional[str] = None

    # User Data (will be needed for ingestion tasks)
    blog_rss_url: Optional[str] = None
    linkedin_profile_url: Optional[str] = None
    twitter_username: Optional[str] = None

    # Environment
    environment: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def get_required_for_task(self, task: str) -> list[str]:
        """Return list of required settings for a specific task."""
        requirements = {
            "aws_basic": ["aws_region"],
            "dynamodb": ["aws_region"],  # AWS auth via SSO or keys
            "bedrock": ["aws_region", "bedrock_kb_id"],
            "blog_scraping": ["blog_rss_url"],
            "classification": ["anthropic_api_key"],
            "letta": ["letta_base_url"],
        }
        return requirements.get(task, [])


# Global settings instance
settings = Settings()

# If AWS_PROFILE is set, ensure it's in the environment for boto3
if settings.aws_profile:
    os.environ["AWS_PROFILE"] = settings.aws_profile
