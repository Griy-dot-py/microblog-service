from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.tables import like, tweet2media

from .base import Base


class Tweet(Base):
    __tablename__ = "tweet"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]

    media: Mapped[list["Media"]] = relationship(  # noqa
        secondary=tweet2media, back_populates="tweets"
    )
    likes: Mapped[list["User"]] = relationship(  # noqa
        secondary=like, back_populates="likes"
    )
