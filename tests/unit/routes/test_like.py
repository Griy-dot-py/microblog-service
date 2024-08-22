from random import choice

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Tweet

URL = "api/tweets/{}/likes"


@pytest.mark.asyncio
async def test_post_like(client: TestClient, users: list[dict], likes: list[dict], test_session: AsyncSession):
    user = choice(users)
    for like in likes:
        if like["user_id"] != user["id"]:
            break
    
    response = client.post(URL.format(like["tweet_id"]), headers={"api-key": user["api_key"]})
    tweet = await test_session.get(Tweet, like["tweet_id"])

    assert response.status_code == 200
    assert user["id"] in {u.id for u in await tweet.awaitable_attrs.likes}


@pytest.mark.asyncio
async def test_delete_like(client: TestClient, users: list[dict], likes: list[dict], test_session: AsyncSession):
    like = choice(likes)
    for user in users:
        if like["user_id"] == user["id"]:
            break
    
    response = client.delete(URL.format(like["tweet_id"]), headers={"api-key": user["api_key"]})
    tweet = await test_session.get(Tweet, like["tweet_id"])

    assert response.status_code == 200
    assert user["id"] not in {u.id for u in await tweet.awaitable_attrs.likes}
