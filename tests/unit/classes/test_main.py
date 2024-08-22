import asyncio
import pytest
from random import choice

from tests import faker
from models import UserProfile
from classes import MicroblogUser, AuthorizedUser
from classes.exc import UserDoesNotExist

loop: asyncio.AbstractEventLoop


def test__init__():
    key = faker.password()
    instance = MicroblogUser(api_key=key)
    assert instance._MicroblogUser__api_key == key


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize("existing", (True, False))
async def test_authorize(users: list[dict], existing: bool):
    global loop

    if existing:
        user = choice(users)
        
        async with MicroblogUser(user["api_key"]).authorize() as auth_user:
            
            assert isinstance(auth_user, AuthorizedUser)
            assert user["id"] == auth_user.id
            assert user["name"] == auth_user.name
    else:  
        with pytest.raises(UserDoesNotExist):
            async with MicroblogUser(faker.password(30)).authorize():
                pass


@pytest.mark.asyncio(loop_scope="module")
async def test_check_profile(users: list[dict], follows: list[dict]):   
    global loop
    
    user = choice(users)
    profile = await MicroblogUser.check_profile(user["id"])
    
    assert isinstance(profile, UserProfile)
    assert profile.id == user["id"]
    assert profile.name == user["name"]
    assert {u.id for u in profile.followers} == {follow["follower_id"] for follow in follows if follow["user_id"] == user["id"]}
    assert {u.id for u in profile.following} == {follow["user_id"] for follow in follows if follow["follower_id"] == user["id"]}
