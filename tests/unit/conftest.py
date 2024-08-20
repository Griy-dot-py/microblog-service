from itertools import permutations
from random import choice

import pytest
import pytest_asyncio
from sqlalchemy import insert

from tests import faker
from database import engine, Session
from database.models import Base, Follow, Media, Tweet, User


@pytest_asyncio.fixture
async def test_session():
    async with Session() as session:
        async with session.begin():
            yield session


@pytest_asyncio.fixture(autouse=True)
async def prepare_db(
    users: list[dict],
    tweets: list[dict],
    follows: list[dict],
    likes: list[dict],
    medias: list[dict],
    tweets2medias: list[dict]
):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with Session() as session:
        async with session.begin():
            await session.execute(insert(User), users)
            await session.flush()
            
            await session.execute(insert(Follow), follows)
            await session.execute(insert(Tweet), tweets)
            await session.execute(insert(Media), medias)
            await session.flush()
            
            for like in likes:
                for user in users:
                    if user["id"] == like["user_id"]:
                        orm_user = await session.get(User, user["id"])
                for tweet in tweets:
                    if tweet["id"] == like["tweet_id"]:
                        orm_tweet = await session.get(Tweet, tweet["id"])
                (await orm_tweet.awaitable_attrs.likes).append(orm_user)
                        
            for tweet2media in tweets2medias:
                for tweet in tweets:
                    if tweet["id"] == tweet2media["tweet_id"]:
                        orm_tweet = await session.get(Tweet, tweet["id"])
                for media in medias:
                    if media["id"] == tweet2media["media_id"]:
                        orm_media = await session.get(Media, media["id"])
                (await orm_tweet.awaitable_attrs.media).append(orm_media)


@pytest.fixture
def users():
    keys = [faker.password(length=12) for _ in range(3)]
    assert len(keys) == len({*keys})
    return [dict(id=id, api_key=key, name=faker.name()) for id, key in zip(range(10, 13), keys)]


@pytest.fixture
def follows(users: list[dict]):
    follow_set = {*permutations([u["id"] for u in users], 2)}
    follows = []
    for _ in range(3):
        follower_id, user_id = follow_set.pop()
        follows.append(dict(follower_id=follower_id, user_id=user_id))
    
    return follows


@pytest.fixture
def tweets(users: list[dict]):
    tweets = [dict(id=10, content=faker.text(), author_id=users[0]["id"], creation_date=faker.date_time())]
    tweets.extend([
        dict(
            id=id,
            content=faker.text(),
            author_id=choice(users)["id"],
            creation_date=faker.date_time()
        ) for id in range(11, 17)
    ])
    
    return tweets


@pytest.fixture
def likes(users: list[dict], tweets: list[dict]):
    id_list = [(users[0]["id"], choice(users)["id"])]
    while len(id_list) < 3:
        ids = (choice(users)["id"], choice(tweets)["id"])
        if ids not in id_list:
            id_list.append(ids)
    return [dict(user_id=user_id, tweet_id=tweet_id) for user_id, tweet_id in id_list]


@pytest.fixture
def medias(users: list[dict]):
    return [
        dict(
            id=id,
            content=faker.image(),
            author_id=choice(users)["id"]
        ) for id in range(10 ,13)
    ]


@pytest.fixture
def tweets2medias(tweets: list[dict], medias: list[dict]):
    id_list = []
    while len(id_list) < 5:
        ids = (choice(tweets)["id"], choice(medias)["id"])
        if ids not in id_list:
            id_list.append(ids)
    return [dict(tweet_id=tweet_id, media_id=media_id) for tweet_id, media_id in id_list]
