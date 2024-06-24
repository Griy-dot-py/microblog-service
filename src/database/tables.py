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
    Column("user_id", ForeignKey("user.id")),
    Column("tweet_id", ForeignKey("tweet.id")),
)

follow = Table(
    "follow",
    Base.metadata,
    Column("user", ForeignKey("user.id")),
    Column("follower", ForeignKey("user.id")),
)
