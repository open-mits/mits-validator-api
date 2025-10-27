"""Configuration management using pydantic-settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service metadata
    app_name: str = Field(default="mits-validator-api", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    environment: str = Field(default="development", description="Environment (dev, staging, prod)")

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8080, description="Server port")
    log_level: str = Field(default="INFO", description="Logging level")

    # Security limits
    max_body_bytes: int = Field(
        default=524_288,  # 512 KB
        description="Maximum request body size in bytes",
        ge=1024,
        le=10_485_760,  # Max 10 MB
    )
    rate_limit: str = Field(
        default="60/minute",
        description="Rate limit per IP (format: count/period, e.g., '60/minute')",
    )
    request_timeout_seconds: int = Field(
        default=2,
        description="Timeout for XML parsing and validation operations",
        ge=1,
        le=30,
    )

    # CORS configuration (comma-separated string or empty)
    allowed_origins: str = Field(
        default="",
        description="Comma-separated list of allowed CORS origins (empty = CORS disabled)",
    )
    
    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse allowed_origins string to list."""
        if not self.allowed_origins:
            return []
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
    allow_credentials: bool = Field(default=False, description="Allow credentials in CORS")
    allowed_methods: str = Field(
        default="POST", description="Comma-separated list of allowed HTTP methods"
    )
    allowed_headers: str = Field(default="*", description="Comma-separated list of allowed headers")
    
    @property
    def allowed_methods_list(self) -> list[str]:
        """Parse allowed_methods string to list."""
        return [m.strip() for m in self.allowed_methods.split(",") if m.strip()]
    
    @property
    def allowed_headers_list(self) -> list[str]:
        """Parse allowed_headers string to list."""
        return [h.strip() for h in self.allowed_headers.split(",") if h.strip()]

    # Feature flags
    enable_docs: bool = Field(default=True, description="Enable OpenAPI documentation")
    enable_rate_limiting: bool = Field(default=True, description="Enable rate limiting")

    # Validation settings
    max_xml_depth: int = Field(
        default=100,
        description="Maximum XML nesting depth to prevent deeply nested attacks",
        ge=10,
        le=1000,
    )
    enable_xml_validation: bool = Field(default=True, description="Enable XML validation")


# Global settings instance
settings = Settings()
