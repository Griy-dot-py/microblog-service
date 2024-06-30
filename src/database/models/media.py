from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.tables import tweet2media

from .base import Base


class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)
    auhor_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    content: Mapped[bytes]

    tweets: Mapped[list["Tweet"]] = relationship(  # noqa
        secondary=tweet2media, back_populates="media"
    )
