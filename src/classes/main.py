from sqlalchemy import select

from database import Session
from database import models as orm

from . import exc
from .abc import MicroblogUserProtocol
from .authorized import AuthorizedUser


class MicroblogUser(MicroblogUserProtocol):
    def __init__(self, api_key: str):
        self.__api_key = api_key

    async def authorize(self) -> AuthorizedUser:
        async with Session() as session:
            if result := await session.scalar(
                select(orm.User).filter_by(api_key=self.__api_key)
            ):
                return AuthorizedUser(orm_model=result)
            else:
                raise exc.UserDoesNotExist(
                    f"User with api key '{self.__api_key}' not found"
                )
