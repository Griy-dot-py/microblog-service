from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


@dataclass
class UserContext:
    session: AsyncSession
    orm: User
