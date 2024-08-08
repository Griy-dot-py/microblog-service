from datetime import datetime, timezone

from pytest import fixture, mark, raises
from sqlalchemy.orm import Session

from database.models import User, Tweet
from models import TweetLoad
from classes import AuthorizedUser
from classes.exc import UserDoesNotExist, TweetDoesNotExist


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
async def test__tweet_context(instance: AuthorizedUser, orm_tweets: list[Tweet], error: bool):
    if not error:
        tweet = orm_tweets[-1]
        async with instance._AuthorizedUser__tweet_context(tweet.id) as context:
            assert tweet.content == context.tweet.content
            assert tweet.author_id == context.tweet.author_id
            assert tweet.creation_date == context.tweet.creation_date
    else:
        unexisting = len(orm_tweets) + 1
        with raises(TweetDoesNotExist):
            async with instance._AuthorizedUser__tweet_context(unexisting):
                pass

@mark.asyncio
async def test_post_tweet(eng, instance: AuthorizedUser, tweet_load: TweetLoad):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    id = await instance.post_tweet(tweet_load)
    with Session(bind=eng) as session:
        orm_tweet = session.get(Tweet, id)
        assert orm_tweet.content == tweet_load.tweet_data
        assert orm_tweet.author_id == instance.id
        assert (orm_tweet.creation_date - now).seconds < 60
        assert {media.id for media in orm_tweet.media} == {*tweet_load.tweet_media_ids}
