from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from database import Session
from database.queries import user
from models import UserProfile

from . import exc
from .abc import MicroblogUserProtocol
from .authorized import AuthorizedUser


class MicroblogUser(MicroblogUserProtocol):
    def __init__(self, api_key: str):
        self.__api_key = api_key

    @asynccontextmanager
    async def authorize(self) -> AsyncGenerator[AuthorizedUser, Any]:
        async with Session() as session:
            async with session.begin():
                if result := await session.scalar(user(self.__api_key)):
                    yield AuthorizedUser(orm_model=result, session=session)
                else:
                    raise exc.UserDoesNotExist(
                        f"User with api key '{self.__api_key}' not found"
                    )

    @classmethod
    async def check_profile(cls, user_id: int) -> UserProfile:
        return await AuthorizedUser.check_user_profile(user_id)
