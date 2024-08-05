from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Tweet


@dataclass
class TweetContext:
    session: AsyncSession
    tweet: Tweet
