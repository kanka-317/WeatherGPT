from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "WeatherGPT"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://weathergpt:weathergpt_secret@db:5432/weathergpt_db"

    # Security
    JWT_SECRET: str = "supersecretjwtkey_change_in_production_min32chars"
    CORS_ORIGINS: Union[List[str], str] = ["*"]

    # External APIs
    OPENAI_API_KEY: str = ""
    OPENWEATHER_API_KEY: str = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def clean_database_url(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().replace("\r", "").replace("\n", "")
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
