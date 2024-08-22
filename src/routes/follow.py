from typing import Annotated

from fastapi import APIRouter, Header

from classes import MicroblogUser
from models import Result

follow = APIRouter(prefix="/users/{id}/follow", tags=["follow"])


@follow.post("")
async def post_follow(api_key: Annotated[str, Header()], id: int) -> Result:
    async with MicroblogUser(api_key=api_key).authorize() as user:
        await user.follow(id)
        return Result()


@follow.delete("")
async def delete_follow(api_key: Annotated[str, Header()], id: int) -> Result:
    async with MicroblogUser(api_key=api_key).authorize() as user:
        await user.stop_following(id)
        return Result()
