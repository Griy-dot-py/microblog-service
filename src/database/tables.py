from sqlalchemy import Column, ForeignKey, Table

from .models import Base

tweet2media = Table(
    "tweet2media",
    Base.metadata,
    Column("tweet_id", ForeignKey("tweet.id")),
    Column("media_id", ForeignKey("media.id")),
)

like = Table(
    "like",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("tweet_id", ForeignKey("tweet.id"), primary_key=True),
)

__all__ = ["tweet2media", "like"]
