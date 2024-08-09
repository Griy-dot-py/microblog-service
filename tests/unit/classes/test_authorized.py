from datetime import datetime, timezone

from pytest import fixture, mark, raises
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from tests import faker, Like
from database.models import User, Tweet, Media
from models import TweetLoad
from classes import AuthorizedUser
from classes.exc import UserDoesNotExist, TweetDoesNotExist, NotOwnTweet


@fixture
def instance(orm_users):
    first, *_ = orm_users
    return AuthorizedUser(orm_model=first)


@mark.asyncio
@mark.parametrize("error", (False, True))
async def test__user_context(instance: AuthorizedUser, orm_users: list[User], error: bool):
    if not error:
        user = orm_users[-1]
        async with instance._AuthorizedUser__user_context(user.id) as context:
            assert user.name == context.user.name
    else:
        unexisting = len(orm_users) + 1
        with raises(UserDoesNotExist):
            async with instance._AuthorizedUser__user_context(unexisting):
                pass


@mark.asyncio
@mark.parametrize("error", (False, True))
async def test__tweet_context(instance: AuthorizedUser, orm_tweets: list[Tweet], error: bool, likes, tweets2medias):
    if not error:
        tweet = orm_tweets[-1]
        async with instance._AuthorizedUser__tweet_context(tweet.id) as context:
            assert tweet.content == context.tweet.content
            assert tweet.author_id == context.tweet.author_id
            assert tweet.creation_date == context.tweet.creation_date
            assert {u.id for u in tweet.likes} == {u.id for u in context.tweet.likes}
            assert {m.id for m in tweet.medias} == {m.id for m in context.tweet.media}
    else:
        unexisting = len(orm_tweets) + 1
        with raises(TweetDoesNotExist):
            async with instance._AuthorizedUser__tweet_context(unexisting):
                pass

@mark.asyncio
async def test_post_tweet(session: Session, instance: AuthorizedUser, tweet_load: TweetLoad):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    id = await instance.post_tweet(tweet_load)
    session.flush()
    
    orm_tweet = session.scalar(select(Tweet).options(joinedload(Tweet.media)).where(Tweet.id == id))
    assert orm_tweet.content == tweet_load.tweet_data
    assert orm_tweet.author_id == instance.id
    assert (orm_tweet.creation_date - now).seconds < 60
    set1, set2 = {media.id for media in orm_tweet.media}, {*tweet_load.tweet_media_ids}
    assert set1 == set2


@mark.asyncio
async def test_add_image(test_session: Session, instance: AuthorizedUser):
    image = faker.image()
    id = await instance.add_image(image)
    
    orm_media = test_session.get(Media, id)
    assert orm_media.author_id == instance.id
    assert orm_media.content == image


@mark.asyncio
@mark.parametrize("error", (False, True))
async def test_del_tweet(test_session: Session, instance: AuthorizedUser, error: bool, orm_tweets):
    if not error:
        self_tweet_id = test_session.scalar(select(Tweet).filter_by(author_id=instance.id)).id
        await instance.del_tweet(self_tweet_id)
        test_session.flush()
        tweet = test_session.get(Tweet, self_tweet_id)
        assert tweet is None
    else:
        non_self_tweet, *_ = test_session.scalars(select(Tweet).where(Tweet.author_id != instance.id))
        with raises(NotOwnTweet):
            await instance.del_tweet(non_self_tweet.id)


@mark.asyncio
async def test_like(test_session: Session, instance: AuthorizedUser, orm_tweets: list[Tweet]):
    tweet_id = test_session.scalar(select(Tweet)).id
    await instance.like(tweet_id)
    test_session.flush()
    tweet = test_session.get(Tweet, tweet_id)
    assert instance.id in {user.id for user in tweet.likes}


@mark.asyncio
async def test_remove_like(test_session: Session, instance: AuthorizedUser, orm_tweets: list[Tweet], likes: list[Like]):
    liked_tweet_id = likes[0].tweet_id
    likers = test_session.get(Tweet, liked_tweet_id).likes
    assert instance.id in {u.id for u in likers}
