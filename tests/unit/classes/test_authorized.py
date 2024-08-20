import asyncio
import pytest
import pytest_asyncio

from random import random
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from tests import faker
from database.models import User, Tweet, Media
from models import TweetLoad
from classes import AuthorizedUser
from classes.exc import UserDoesNotExist, TweetDoesNotExist, NotOwnTweet

loop: asyncio.AbstractEventLoop


@pytest_asyncio.fixture
async def instance(test_session: AsyncSession, users: list[dict]):
    global loop

    model = await test_session.get(User, users[0]["id"])
    return AuthorizedUser(orm_model=model, session=test_session)


@pytest_asyncio.fixture
async def tweet_load(medias: list[dict]):
    media_ids = {media["id"] for media in medias}
    added = []
    for _ in range(2):
        if random() < 5:
            added.append(media_ids.pop())
    return TweetLoad(tweet_data=faker.text(), tweet_media_ids=added)


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize("error", (False, True))
async def test__get_user(instance: AuthorizedUser, users: list[dict], test_session: AsyncSession, error: bool):
    global loop
    
    if not error:
        existing = await test_session.get(User, users[-1]["id"])
        user = await instance._AuthorizedUser__get_user(existing.id)
        assert existing.name == user.name
    else:
        unexisting_id = len(users) + 1
        with pytest.raises(UserDoesNotExist):
            await instance._AuthorizedUser__get_user(unexisting_id)


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize("error", (False, True))
async def test__get_tweet(instance: AuthorizedUser, tweets: list[dict], test_session: AsyncSession, error: bool):
    global loop
    
    if not error:
        existing = await test_session.get(Tweet, tweets[-1]["id"])
        tweet = await instance._AuthorizedUser__get_tweet(existing.id)
        assert existing.content == tweet.content
        assert existing.author_id == tweet.author_id
        assert existing.creation_date == tweet.creation_date
        assert {u.id for u in existing.likes} == {u.id for u in await tweet.awaitable_attrs.likes}
        assert {m.id for m in await existing.awaitable_attrs.media} == {m.id for m in await tweet.awaitable_attrs.media}
    else:
        unexisting_id = len(tweets) + 1
        with pytest.raises(TweetDoesNotExist):
            await instance._AuthorizedUser__get_tweet(unexisting_id)


@pytest.mark.asyncio(loop_scope="module")
async def test_post_tweet(instance: AuthorizedUser, tweet_load: TweetLoad, test_session: AsyncSession):
    global loop
    
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    id = await instance.post_tweet(tweet_load)
    
    orm_tweet = await test_session.get(Tweet, id)
    assert orm_tweet.content == tweet_load.tweet_data
    assert orm_tweet.author_id == instance.id
    assert (now - orm_tweet.creation_date).seconds < 60
    assert {media.id for media in await orm_tweet.awaitable_attrs.media} == {*tweet_load.tweet_media_ids}


@pytest.mark.asyncio(loop_scope="module")
async def test_add_image(instance: AuthorizedUser, test_session: AsyncSession):
    global loop
    
    image = faker.image()
    id = await instance.add_image(image)
    
    orm_media = await test_session.get(Media, id)
    assert orm_media.author_id == instance.id
    assert orm_media.content == image


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize("error", (False, True))
async def test_del_tweet(instance: AuthorizedUser, error: bool, tweets: list[dict], test_session: AsyncSession):
    global loop
    
    if not error:
        for tweet in tweets:
            if tweet["author_id"] == instance.id:
                break
        
        await instance.del_tweet(tweet["id"])
        
        assert await test_session.get(Tweet, tweet["id"]) is None
    else:
        for tweet in tweets:
            if tweet["author_id"] != instance.id:
                id = tweet["id"]
        with pytest.raises(NotOwnTweet):
            await instance.del_tweet(id)


@pytest.mark.asyncio(loop_scope="module")
async def test_like(instance: AuthorizedUser, likes: list[dict], test_session: AsyncSession):
    global loop
    
    for like in likes:
        if like["user_id"] == instance.id:
            break
    
    await instance.like(like["tweet_id"])
    
    orm_tweet = await test_session.get(Tweet, like["tweet_id"])
    assert instance.id in {user.id for user in await orm_tweet.awaitable_attrs.likes}


@pytest.mark.asyncio(loop_scope="module")
async def test_remove_like(instance: AuthorizedUser, likes: list[dict], test_session: AsyncSession):
    global loop
    
    for like in likes:
        if like["user_id"] == instance.id:
            break
    
    await instance.remove_like(like["tweet_id"])
    
    orm_tweet = await test_session.get(Tweet, like["tweet_id"])
    assert instance.id not in {user.id for user in await orm_tweet.awaitable_attrs.likes}
