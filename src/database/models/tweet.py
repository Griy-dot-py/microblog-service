from datetime import datetime

from sqlalchemy import ForeignKey, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.tables import like, tweet2media

from .base import Base


class Tweet(Base):
    __tablename__ = "tweet"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    creation_date: Mapped[datetime] = mapped_column(default=select(func.now()))

    media: Mapped[list["Media"]] = relationship(  # noqa
        secondary=tweet2media, back_populates="tweets"
    )
    likes: Mapped[list["User"]] = relationship(  # noqa
        secondary=like, back_populates="likes"
    )
    author: Mapped["User"] = relationship(back_populates="tweets")  # noqa
