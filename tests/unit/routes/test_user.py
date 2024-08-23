from random import choice

import pytest
from fastapi.testclient import TestClient

URL = "/api/users"


@pytest.mark.asyncio
async def test_get_me(client: TestClient, users: list[dict], follows: list[dict]):
    user = choice(users)
    
    response = client.get(URL + "/me", headers={"api-key": user["api_key"]})
    assert response.status_code == 200
    
    profile: dict[str, str | list | dict] = response.json()["user"]
    assert profile["id"] == user["id"]
    assert profile["name"] == user["name"]
    assert {u["id"] for u in profile["followers"]} == {follow["follower_id"] for follow in follows if follow["user_id"] == user["id"]}
    assert {u["id"] for u in profile["following"]} == {follow["user_id"] for follow in follows if follow["follower_id"] == user["id"]}


@pytest.mark.asyncio
async def test_get_user(client: TestClient, users: list[dict], follows: list[dict]):
    user = choice(users)
    
    response = client.get(URL + f"/{user["id"]}")
    assert response.status_code == 200
    
    profile: dict[str, str | list | dict] = response.json()["user"]
    assert profile["id"] == user["id"]
    assert profile["name"] == user["name"]
    assert {u["id"] for u in profile["followers"]} == {follow["follower_id"] for follow in follows if follow["user_id"] == user["id"]}
    assert {u["id"] for u in profile["following"]} == {follow["user_id"] for follow in follows if follow["follower_id"] == user["id"]}
