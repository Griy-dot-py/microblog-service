from typing import Annotated

from fastapi import APIRouter, Header

from classes import MicroblogUser
from models import GetProfileDump

users = APIRouter(prefix="/users", tags=["user"])


@users.get("/me")
async def get_me(api_key: Annotated[str, Header()]) -> GetProfileDump:
    async with MicroblogUser(api_key=api_key).authorize() as user:
        return GetProfileDump(user=await user.check_profile())


@users.get("/{id}")
async def get_user(id: int) -> GetProfileDump:
    return GetProfileDump(user=await MicroblogUser.check_profile(id))
