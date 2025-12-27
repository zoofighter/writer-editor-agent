"""
Application settings and configuration management.

Uses Pydantic Settings for type-safe configuration with environment variable support.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    All settings can be overridden via environment variables or a .env file.
    Environment variable names are uppercase versions of field names.

    Example:
        LM_STUDIO_BASE_URL=http://localhost:1234/v1
    """

    # LM Studio Configuration
    lm_studio_base_url: str = "http://localhost:1234/v1"
    lm_studio_model: str = "qwen"

    # Generation Parameters
    writer_temperature: float = 0.8  # Higher temperature for more creative writing
    editor_temperature: float = 0.3  # Lower temperature for more analytical feedback
    max_tokens: int = 2000

    # Workflow Configuration
    max_iterations: int = 10

    # Database Configuration
    checkpoint_db_path: str = "data/checkpoints.sqlite"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton instance
settings = Settings()
