import asyncio
import pytest
import pytest_asyncio

from random import choice
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tests import faker
from database.models import User, Tweet, Media, Follow
from models import TweetLoad, TweetDump, UserProfile
from classes import AuthorizedUser
from classes.exc import UserDoesNotExist, TweetDoesNotExist, NotOwnTweet

loop: asyncio.AbstractEventLoop


@pytest_asyncio.fixture
async def instance(test_session: AsyncSession, users: list[dict]):
    global loop

    model = await test_session.get(User, users[0]["id"])
    return AuthorizedUser(orm_model=model, session=test_session)


@pytest.mark.asyncio(loop_scope="module")
async def test__init__(test_session: AsyncSession, users: list[dict]):
    global loop
    
    user = choice(users)
    model = await test_session.get(User, user["id"])
    instance = AuthorizedUser(orm_model=model, session=test_session)
    assert instance._AuthorizedUser__orm is model
    assert instance._AuthorizedUser__session is test_session


def test_id(instance: AuthorizedUser):
    assert instance.id == instance._AuthorizedUser__orm.id


def test_name(instance: AuthorizedUser):
    assert instance.name == instance._AuthorizedUser__orm.name


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
        if like["user_id"] != instance.id:
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


@pytest.mark.asyncio(loop_scope="module")
async def test_follow(instance: AuthorizedUser, follows: list[dict], test_session: AsyncSession):
    global loop
    
    for follow in follows:
        if follow["follower_id"] != instance.id:
            break
    
    await instance.follow(follow["user_id"])
    
    assert await test_session.get(Follow, (instance.id, follow["user_id"]))


@pytest.mark.asyncio(loop_scope="module")
async def test_stop_following(instance: AuthorizedUser, follows: list[dict], test_session: AsyncSession):
    global loop
    
    for follow in follows:
        if follow["follower_id"] == instance.id:
            break
    
    await instance.stop_following(follow["user_id"])
    
    assert not await test_session.get(Follow, (follow["follower_id"], follow["user_id"]))


@pytest.mark.asyncio(loop_scope="module")
async def test_generate_feed(instance: AuthorizedUser, test_session: AsyncSession):
    global loop
    
    feed = await instance.generate_feed()
    tweet_order = tuple([tweet.id for tweet in feed])
    expected_order = tuple(await test_session.scalars(
        select(Tweet.id)
        .join(Follow, Follow.user_id == Tweet.author_id)
        .where(Follow.follower_id == instance.id)
        .order_by(Tweet.creation_date.desc())
    ))
    rand_tweet = choice(feed)
    rand_tweet_orm = await test_session.get(Tweet, rand_tweet.id)
    
    assert isinstance(rand_tweet, TweetDump)
    assert rand_tweet.author.id == rand_tweet_orm.author_id
    # assert rand_tweet.attachments
    assert rand_tweet.content == rand_tweet_orm.content
    assert {like.user_id for like in rand_tweet.like} == {u.id for u in await rand_tweet_orm.awaitable_attrs.likes}
    assert tweet_order == expected_order


@pytest.mark.asyncio(loop_scope="module")
async def test_check_profile(instance: AuthorizedUser, test_session: AsyncSession):
    global loop
    
    profile = await instance.check_profile()
    followers = await test_session.scalars(
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.user_id == instance.id)
    )
    follows = await test_session.scalars(
        select(User)
        .join(Follow, Follow.user_id == User.id)
        .where(Follow.follower_id == instance.id)
    )
    
    assert isinstance(profile, UserProfile)
    assert profile.id == instance.id
    assert profile.name == instance.name
    assert {u.id for u in profile.followers} == {u.id for u in followers}
    assert {u.id for u in profile.following} == {u.id for u in follows}


@pytest.mark.asyncio(loop_scope="module")
async def test_check_user_profile(users: list[dict], follows: list[dict]):
    global loop
    
    user = choice(users)
    profile = await AuthorizedUser.check_user_profile(user["id"])
    
    assert isinstance(profile, UserProfile)
    assert profile.id == user["id"]
    assert profile.name == user["name"]
    assert {u.id for u in profile.followers} == {follow["follower_id"] for follow in follows if follow["user_id"] == user["id"]}
    assert {u.id for u in profile.following} == {follow["user_id"] for follow in follows if follow["follower_id"] == user["id"]}
