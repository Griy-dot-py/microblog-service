from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from config import settings

from .url import SQLAlchemyURL

url = SQLAlchemyURL(
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host=settings.POSTGRES_HOST,
    db=settings.POSTGRES_DB,
)
engine = create_async_engine(url.concatenate(), echo=True, poolclass=NullPool)if settings.TEST_MODE else create_async_engine(url.concatenate())
Session = async_sessionmaker(bind=engine)
