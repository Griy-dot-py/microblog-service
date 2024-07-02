from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)
    auhor_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    content: Mapped[bytes]
