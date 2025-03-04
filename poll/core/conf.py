import logging
from urllib.parse import quote

from fastapi import HTTPException
from pydantic import PostgresDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str
    postgres_user: SecretStr
    postgres_password: SecretStr

    db_host: str = "db"
    echo_query: bool = True
    db_port: int = 5432

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: SecretStr | None = None

    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

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

    @property
    def redis_connection_uri(self) -> str | None:
        return str(
            RedisDsn.build(
                scheme="redis",
                host=self.redis_host,
                port=self.redis_port,
                password=(
                    self.redis_password.get_secret_value()
                    if self.redis_password
                    else None
                ),
                path=f"/{self.redis_db}",
            )
        )

    def get_log_level(self) -> int:
        return {
            "info": logging.INFO,
            "debug": logging.DEBUG,
            "error": logging.ERROR,
        }.get(self.log_level.lower(), logging.INFO)


settings = Settings()
