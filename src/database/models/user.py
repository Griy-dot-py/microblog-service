from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__ = "user"
    __table_args__ = (UniqueConstraint("api_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    api_key: Mapped[str]
    name: Mapped[str]
