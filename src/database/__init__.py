from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings

from .url import SQLAlchemyURL

url = SQLAlchemyURL(
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host=settings.POSTGRES_HOST,
    db=settings.POSTGRES_DB,
)
engine = create_async_engine(url.concatenate(), echo=True)
Session = async_sessionmaker(bind=engine)


@asynccontextmanager
async def transaction() -> AsyncGenerator[AsyncSession, Any]:
    async with Session() as session:
        async with session.begin():
            yield session


async def dispose():
    await engine.dispose()
