from itertools import permutations
from random import choice

from pytest import fixture, mark
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from . import faker, Like, Tweet2Media
from .config import test_settings
from database import models
import database


@fixture
def orm_users():
    while True:
        passwords = [faker.password(length=12) for _ in range(3)]
        names = [faker.name() for _ in range(3)]
        if len(passwords) == len({*passwords}) and len(names) == len({*names}):
            break
    return [models.User(id=id, api_key=passw, name=name) for id, passw, name in zip(range(3), passwords, names)]


@fixture
def orm_follows(orm_users):
    follow_set = {*permutations(orm_users, 2)}
    return [follow_set.pop() for _ in range(3)]


@fixture
def orm_tweets(orm_users):
    tweets = [
        models.Tweet(
            id=id,
            content=faker.text(),
            author_id=choice(orm_users).id,
            creation_date=faker.date_time()
        ) for id in range(7)
    ]
    tweets.sort(key=lambda tweet: tweet.creation_date)
    return tweets


@fixture
def likes(orm_users, orm_tweets):
    likes = []
    while len(likes) < 3:
        ids = (choice(orm_users).id, choice(orm_tweets).id)
        if ids not in likes:
            likes.append(ids)
    return [Like(user_id=user_id, tweet_id=tweet_id) for user_id, tweet_id in likes]


@fixture
def orm_medias(orm_users):
    return [models.Media(id=id, content=faker.image(), author_id=choice(orm_users).id) for id in range(3)]


@fixture
def tweets2medias(orm_tweets, orm_medias):
    tuples = []
    while len(tuple) < 5:
        ids = (choice(orm_tweets).id, choice(orm_medias).id)
        if ids not in tuples:
            tuples.append(ids)
    return [Tweet2Media(tweet_id=tweet_id, media_id=media_id) for tweet_id, media_id in tuples]


@fixture(scope="session")
@mark.asyncio
async def engine():
    url = "{dialect}+{driver}://{user}:{passw}@{host}:{port}/{db}".format(
        user=test_settings.POSTGRES_USER,
        passw=test_settings.POSTGRES_PASSWORD,
        host=test_settings.POSTGRES_HOST,
        db=test_settings.POSTGRES_DB,
        dialect="postgresql",
        driver="asyncpg",
        port=5432,
    )
    eng = create_async_engine(url)
    yield eng
    
    await eng.dispose()


@fixture
@mark.asyncio
async def session(engine):
    async with AsyncSession(bind=engine) as session:
        yield session



@fixture(autouse=True)
@mark.asyncio
async def db(
    engine,
    session,
    orm_follows,
    likes,
    orm_medias,
    orm_tweets,
    tweets2medias,
    orm_users
):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    try:
        async with session.begin():
            await session.add_all(orm_users)
            await session.flush()
            await session.add_all([*orm_tweets, *orm_follows, *orm_medias])
            await session.flush()
            for like in likes:
                tweet: models.Tweet = orm_tweets[like.tweet_id]
                user: models.User = orm_users[like.user_id]
                tweet.likes.append(user)
            for tweet2media in tweets2medias:
                tweet: models.Tweet = orm_tweets[tweet2media.tweet_id]
                media: models.Media = orm_medias[tweet2media.media_id]
                tweet.media.append(media)
        
        database.engine = engine
        database.Session = async_sessionmaker(bind=engine)
        yield

    finally:
        async with engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.drop_all)
