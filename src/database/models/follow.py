from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Follow(Base):
    __tablename__ = "follow"
    
    follower_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
