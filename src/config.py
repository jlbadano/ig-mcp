"""
Configuration management for Instagram MCP Server.
"""

from pathlib import Path
from typing import List, Optional

from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings


class InstagramMCPSettings(BaseSettings):
    """Instagram MCP Server configuration settings."""

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # Instagram API Configuration
    instagram_access_token: str = Field(..., description="Instagram access token")
    facebook_app_id: str = Field(..., description="Facebook app ID")
    facebook_app_secret: str = Field(..., description="Facebook app secret")
    instagram_business_account_id: Optional[str] = Field(
        None, description="Instagram business account ID"
    )

    # API Configuration
    instagram_api_version: str = Field("v19.0", description="Instagram API version")
    instagram_api_base_url: str = Field(
        "https://graph.facebook.com", description="Instagram API base URL"
    )

    # Rate Limiting Configuration
    rate_limit_requests_per_hour: int = Field(
        200, description="Rate limit requests per hour"
    )
    rate_limit_posts_per_day: int = Field(25, description="Rate limit posts per day")
    rate_limit_enable_backoff: bool = Field(
        True, description="Enable rate limit backoff"
    )

    # Logging Configuration
    log_level: str = Field("INFO", description="Log level")
    log_format: str = Field("json", description="Log format")
    log_file: Optional[str] = Field(
        "logs/instagram_mcp.log", description="Log file path"
    )

    # Cache Configuration
    cache_enabled: bool = Field(True, description="Enable caching")
    cache_ttl_seconds: int = Field(300, description="Cache TTL in seconds")
    redis_url: Optional[str] = Field(
        "redis://localhost:6379/0", description="Redis URL"
    )

    # Security Configuration
    enable_request_validation: bool = Field(
        True, description="Enable request validation"
    )
    max_request_size_mb: int = Field(10, description="Max request size in MB")
    allowed_image_formats: List[str] = Field(
        ["jpg", "jpeg", "png", "gif"], description="Allowed image formats"
    )
    allowed_video_formats: List[str] = Field(
        ["mp4", "mov"], description="Allowed video formats"
    )

    # Development Configuration
    debug_mode: bool = Field(False, description="Debug mode")
    mock_api_responses: bool = Field(False, description="Mock API responses")
    enable_metrics: bool = Field(True, description="Enable metrics")

    # MCP Server Configuration
    mcp_server_name: str = Field("instagram-mcp-server", description="MCP server name")
    mcp_server_version: str = Field("1.0.0", description="MCP server version")
    mcp_transport: str = Field("stdio", description="MCP transport")

    # Optional: Database Configuration
    database_url: Optional[str] = Field(
        "sqlite:///instagram_mcp.db", description="Database URL"
    )
    database_echo: bool = Field(False, description="Database echo")

    # Optional: Webhook Configuration
    webhook_verify_token: Optional[str] = Field(
        None, description="Webhook verify token"
    )
    webhook_secret: Optional[str] = Field(None, description="Webhook secret")
    webhook_url: Optional[str] = Field(None, description="Webhook URL")

    @field_validator("allowed_image_formats", "allowed_video_formats", mode="before")
    @classmethod
    def parse_list_from_string(cls, v):
        """Parse comma-separated string into list."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v):
        """Validate log format."""
        valid_formats = ["json", "text"]
        if v.lower() not in valid_formats:
            raise ValueError(f"Log format must be one of: {valid_formats}")
        return v.lower()

    @field_validator("instagram_api_version")
    @classmethod
    def validate_api_version(cls, v):
        """Validate Instagram API version format."""
        if not v.startswith("v"):
            raise ValueError("API version must start with 'v' (e.g., 'v19.0')")
        return v

    @property
    def instagram_api_url(self) -> str:
        """Get the full Instagram API URL."""
        return f"{self.instagram_api_base_url}/{self.instagram_api_version}"

    @property
    def log_file_path(self) -> Optional[Path]:
        """Get log file path as Path object."""
        if self.log_file:
            path = Path(self.log_file)
            # Create directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            return path
        return None

    @property
    def max_request_size_bytes(self) -> int:
        """Get max request size in bytes."""
        return self.max_request_size_mb * 1024 * 1024


# Global settings instance - will be None until first access
_settings: Optional[InstagramMCPSettings] = None


def get_settings() -> InstagramMCPSettings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = InstagramMCPSettings()
    return _settings


def reload_settings() -> InstagramMCPSettings:
    """Reload settings from environment variables."""
    global _settings
    _settings = InstagramMCPSettings()
    return _settings
