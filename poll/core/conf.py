import urllib
from typing import Any

from pydantic import PostgresDsn, SecretStr, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    postgres_db: str
    postgres_user: SecretStr
    postgres_password: SecretStr

    db_host: str = 'db'
    echo_query: bool = True
    db_port: int = 5432

    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]


    db_connection_uri: PostgresDsn | None = None

    @field_validator("db_connection_uri", mode="before")
    def assemble_db_connection_uri(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            host=info.data.get("db_host"),
            port=int(info.data.get("db_port")),  # type: ignore
            path=info.data.get("postgres_db"),
            username=info.data.get("postgres_user").get_secret_value(),  # type: ignore[union-attr]
            password=urllib.parse.quote(info.data.get("postgres_password").get_secret_value()),
            # type: ignore[union-attr]
        )



settings = Settings()
