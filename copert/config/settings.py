"""Application settings and configuration."""

import os
import sys
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 4096

    # Application Configuration
    max_iterations: int = 25
    verbose: bool = False

    # LangSmith Configuration
    langsmith_api_key: str

    # Exa Configuration
    exa_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env.copert",  # Use dedicated config file
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
try:
    settings = Settings()
except ValidationError as e:
    print("❌ Error: Missing required environment variables.", file=sys.stderr)
    print(f"\nPlease create a .env.copert file in the current directory ({os.getcwd()}) with:", file=sys.stderr)
    print("  OPENAI_API_KEY=your_openai_api_key", file=sys.stderr)
    print("  LANGSMITH_API_KEY=your_langsmith_api_key", file=sys.stderr)
    print("  EXA_API_KEY=your_exa_api_key", file=sys.stderr)
    print("\nOr set these as environment variables.", file=sys.stderr)
    print("\nExample .env.copert file:", file=sys.stderr)
    print("  OPENAI_API_KEY=sk-...", file=sys.stderr)
    print("  LANGSMITH_API_KEY=lsv2_pt_...", file=sys.stderr)
    print("  EXA_API_KEY=...", file=sys.stderr)
    sys.exit(1)
