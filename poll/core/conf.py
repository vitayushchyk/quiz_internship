import logging
from urllib.parse import quote

from fastapi import HTTPException
from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str
    postgres_user: SecretStr
    postgres_password: SecretStr

    db_host: str = "db"
    echo_query: bool = True
    db_port: int = 5432

    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    log_level: str = "INFO"

    @property
    def db_connection_uri(self) -> PostgresDsn | None:
        if self.postgres_db is None:
            raise HTTPException(
                status_code=500, detail="Missing required setting: postgres_db"
            )
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            path=self.postgres_db,
            username=self.postgres_user.get_secret_value(),
            password=quote(self.postgres_password.get_secret_value()),
        )
        # type: ignore[union-attr]

    def get_log_level(self) -> int:
        return {
            "info": logging.INFO,
            "debug": logging.DEBUG,
            "error": logging.ERROR,
        }.get(self.log_level.lower(), logging.INFO)


settings = Settings()
