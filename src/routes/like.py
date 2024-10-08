from typing import Annotated

from fastapi import APIRouter, Header

from classes import MicroblogUser
from models import Result

likes = APIRouter(prefix="/tweets/{id}/likes", tags=["like"])


@likes.post("")
async def post_like(api_key: Annotated[str, Header()], id: int) -> Result:
    async with MicroblogUser(api_key=api_key).authorize() as user:
        await user.like(id)
        return Result()


@likes.delete("")
async def delete_like(api_key: Annotated[str, Header()], id: int) -> Result:
    async with MicroblogUser(api_key=api_key).authorize() as user:
        await user.remove_like(id)
        return Result()
