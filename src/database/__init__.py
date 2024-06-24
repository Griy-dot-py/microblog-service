from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import config.postgres as config

from .url import SQLAlchemyURL

url = SQLAlchemyURL(
    user=config.USER,
    password=config.PASSWORD,
    host=config.HOST,
    db=config.DB,
)
engine = create_async_engine(url.concatenate())
Session = async_sessionmaker(bind=engine)


async def dispose():
    await engine.dispose()
