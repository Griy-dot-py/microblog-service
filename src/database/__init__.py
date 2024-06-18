import asyncio

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import config.postgres as config

SQLALCHEMY_URL = "{dialect}+{driver}://{user}:{pas}@{host}:{port}/{db}".format(
    dialect="postgresql",
    driver="asyncpg",
    user=config.USER,
    pas=config.PASSWORD,
    host=config.HOST,
    port=config.PORT,
    db=config.DB,
)
engine = create_async_engine(SQLALCHEMY_URL)
Session = async_sessionmaker(bind=engine)


async def main(metadata: MetaData):
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


async def tear_down():
    await engine.dispose()


from .base import Base  # noqa

asyncio.run(main(Base.metadata))
