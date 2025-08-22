from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    database_url: str = Field(
        default="sqlite:///./data/app.db",
        description="Database URL"
    )

    debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    api_v1_str: str = Field(default="/api/v1", description="API v1 prefix")

    host: str = Field(default="0.0.0.0", description="Host to bind")
    port: int = Field(default=8000, description="Port to bind")

    title: str = Field(default="Saber Task API", description="API title")
    version: str = Field(default="1.0.0", description="API version")
    description: str = Field(
        default="A production-ready task management API built with FastAPI",
        description="API description"
    )

    default_page_size: int = Field(default=10, description="Default page size")
    max_page_size: int = Field(default=50, description="Maximum page size")

    allowed_hosts: list[str] = Field(default=["*"], description="Allowed hosts")

    @field_validator('allowed_hosts', mode='before')
    @classmethod
    def parse_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(',')]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
