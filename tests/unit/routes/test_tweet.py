from random import choice
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import TweetLoad
from database.models import Tweet, Follow


URL = "/api/tweets"


@pytest.mark.asyncio
async def test_post_tweet(client: TestClient, users: list[dict], tweet_load: TweetLoad, test_session: AsyncSession):
    user = choice(users)
    
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    response = client.post(URL, headers={"api-key": user["api_key"]}, json=tweet_load.model_dump())
    assert response.status_code == 200
    
    tweet = await test_session.get(Tweet, response.json()["tweet_id"])
    assert tweet.content == tweet_load.tweet_data
    assert tweet.author_id == user["id"]
    assert (tweet.creation_date - now).seconds < 60
    assert {media.id for media in await tweet.awaitable_attrs.media} == {*tweet_load.tweet_media_ids}


@pytest.mark.asyncio
async def test_delete_tweet(client: TestClient, users: list[dict], tweets: list[dict], test_session: AsyncSession):
    tweet = choice(tweets)
    for user in users:
        if user["id"] == tweet["author_id"]:
            break
    
    response = client.delete(URL + f"/{tweet["id"]}", headers={"api-key": user["api_key"]})
    assert response.status_code == 200
    assert not await test_session.get(Tweet, tweet["id"])


@pytest.mark.asyncio
async def test_get_feed(client: TestClient, users: list[dict], follows: list[dict], test_session: AsyncSession):
    user_id = choice(follows)["follower_id"]
    for user in users:
        if user["id"] == user_id:
            break
    
    response = client.get(URL, headers={"api-key": user["api_key"]})
    assert response.status_code == 200
    
    feed: list[dict] = response.json()["tweets"]
    assert isinstance(feed, list)
    tweet_order = tuple([tweet["id"] for tweet in feed])
    expected_order = tuple(await test_session.scalars(
        select(Tweet.id)
        .join(Follow, Follow.user_id == Tweet.author_id)
        .where(Follow.follower_id == user_id)
        .order_by(Tweet.creation_date.desc())
    ))
    rand_tweet: dict[str, dict | str | list] = choice(feed)
    rand_tweet_orm = await test_session.get(Tweet, rand_tweet["id"])
    
    assert rand_tweet["author"]["id"] == rand_tweet_orm.author_id
    # assert rand_tweet.attachments
    assert rand_tweet["content"] == rand_tweet_orm.content
    assert {like["user_id"] for like in rand_tweet["like"]} == {u.id for u in await rand_tweet_orm.awaitable_attrs.likes}
    assert tweet_order == expected_order
