from random import choice

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient

from database.models import Follow


URL = "/api/users/{}/follow"


@pytest.mark.asyncio
async def test_post_follow(client: TestClient, users: list[dict], follows: list[dict], test_session: AsyncSession):
    user = choice(users)
    for follow in follows:
        if user["id"] != follow["follower_id"]:
            break
    
    response = client.post(URL.format(follow["user_id"]), headers={"api-key": user["api_key"]})
    
    assert response.status_code == 200
    assert await test_session.get(Follow, (user["id"], follow["user_id"]))


@pytest.mark.asyncio
async def test_delete_follow(client: TestClient, users: list[dict], follows: list[dict], test_session: AsyncSession):
    follow = choice(follows)
    for user in users:
        if follow["follower_id"] == user["id"]:
            break
    
    response = client.delete(URL.format(follow["user_id"]), headers={"api-key": user["api_key"]})
    
    assert response.status_code == 200
    assert not await test_session.get(Follow, (user["id"], follow["user_id"]))
