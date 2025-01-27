"""Configuration"""

from typing import Annotated, Any

from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_scopes(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    """Configuration"""

    model_config = SettingsConfigDict(
        # Use top level .env file
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    OAUTH_CREDENTIALS_FILE_PATH: str
    OAUTH_TOKEN_FILE_PATH: str
    SCOPES: Annotated[list[str], BeforeValidator(parse_scopes)] = []


settings = Settings()  # type: ignore
