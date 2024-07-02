from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.tables import like

from .base import Base


class User(Base):
    __tablename__ = "user"
    __table_args__ = (UniqueConstraint("api_key"), )

    id: Mapped[int] = mapped_column(primary_key=True)
    api_key: Mapped[str]
    name: Mapped[str]

    likes: Mapped[list["Tweet"]] = relationship(  # noqa
        secondary=like, back_populates="likes"
    )
    tweets: Mapped[list["Tweet"]] = relationship(back_populates="author")  # noqa
