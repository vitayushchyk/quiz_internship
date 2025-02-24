from typing import Annotated, AsyncGenerator

from fastapi import Depends
from redis.asyncio import ConnectionPool as RedisConnectionPool
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from poll.core.conf import settings

engine = create_async_engine(
    url=settings.db_connection_uri.unicode_string(),  # type: ignore[union-attr]
    echo=settings.echo_query,
    future=True,
)

Base = declarative_base()

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


pool = RedisConnectionPool.from_url(settings.redis_connection_uri)
redis = Redis(connection_pool=pool)

DBSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]


async def get_redis_client() -> Redis:
    return redis


RedisDependency = Annotated[Redis, Depends(get_redis_client)]
