"""
Application settings and configuration management.

Uses Pydantic Settings for type-safe configuration with environment variable support.
"""

from typing import Optional
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

    # Generation Parameters - Agent-specific temperatures
    business_analyst_temperature: float = 0.2  # Analytical for intent analysis
    content_strategist_temperature: float = 0.5  # Balanced for outline creation
    outline_reviewer_temperature: float = 0.2  # Analytical for review
    writer_temperature: float = 0.8  # Creative for writing
    editor_temperature: float = 0.3  # Analytical for editing
    max_tokens: int = 2000

    # Workflow Configuration
    max_iterations: int = 10  # Maximum draft revision iterations
    max_outline_revisions: int = 3  # Maximum outline revision iterations

    # Web Search Configuration
    search_provider: str = "duckduckgo"  # Options: duckduckgo, tavily, serper
    search_api_key: Optional[str] = None  # Required for tavily and serper
    max_search_results_per_query: int = 5
    enable_web_search: bool = True  # Can disable for testing without search

    # Database Configuration
    checkpoint_db_path: str = "data/checkpoints.sqlite"

    # Tutorial Book Extension Settings
    code_example_temperature: float = 0.2  # Precision for code generation
    exercise_generator_temperature: float = 0.4  # Moderate for exercise variety
    tutorial_output_dir: str = "output/tutorial"  # Export directory for chapters
    auto_export_chapters: bool = True  # Auto-export on workflow completion
    validate_code_examples: bool = True  # Validate generated code syntax
    max_code_line_length: int = 79  # PEP 8 line length limit
    mc_questions_per_chapter: int = 4  # Multiple choice questions
    fill_in_blank_per_chapter: int = 3  # Fill-in-the-blank exercises
    coding_challenges_per_chapter: int = 3  # Coding challenges

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton instance
settings = Settings()
