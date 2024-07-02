from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import config.postgres as config

from .url import SQLAlchemyURL

url = SQLAlchemyURL(
    user=config.USER,
    password=config.PASSWORD,
    host=config.HOST,
    db=config.DB,
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
