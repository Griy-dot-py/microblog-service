from datetime import datetime

from sqlalchemy import ForeignKey, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..tables import like, tweet2media
from .base import Base
from .media import Media
from .user import User


class Tweet(Base):
    __tablename__ = "tweet"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    creation_date: Mapped[datetime] = mapped_column(default=select(func.now()))

    media: Mapped[list[Media]] = relationship(secondary=tweet2media)
    likes: Mapped[list[User]] = relationship(secondary=like)
    author: Mapped[User] = relationship()
