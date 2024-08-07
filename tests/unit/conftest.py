from itertools import permutations
from random import choice

from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import settings
from tests import faker, Like, Tweet2Media
from database.models import Base, Follow, Media, Tweet, User


@fixture
def orm_users():
    keys = [faker.password(length=12) for _ in range(3)]
    assert len(keys) == len({*keys})
    return [User(id=id, api_key=key, name=faker.name()) for id, key in zip(range(3), keys)]


@fixture
def orm_follows(orm_users):
    follow_set = {*permutations(orm_users, 2)}
    follows = []
    for _ in range(3):
        follower, user = follow_set.pop()
        follows.append(Follow(follower_id=follower.id, user_id=user.id))
    
    return follows


@fixture
def orm_tweets(orm_users):
    tweets = [
        Tweet(
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
    return [Media(id=id, content=faker.image(), author_id=choice(orm_users).id) for id in range(3)]


@fixture
def tweets2medias(orm_tweets, orm_medias):
    tuples = []
    while len(tuples) < 5:
        ids = (choice(orm_tweets).id, choice(orm_medias).id)
        if ids not in tuples:
            tuples.append(ids)
    return [Tweet2Media(tweet_id=tweet_id, media_id=media_id) for tweet_id, media_id in tuples]


@fixture(scope="session")
def engine():
    url = "postgresql+psycopg2://{user}:{passw}@{host}:5432/{db}".format(
        user=settings.POSTGRES_USER,
        passw=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        db=settings.POSTGRES_DB,
    )
    eng = create_engine(url)
    yield eng
    eng.dispose()


@fixture
def session(engine):
    with Session(bind=engine) as session:
        yield session


@fixture(autouse=True)
def prepare_db(
    engine,
    session,
    orm_follows,
    likes,
    orm_medias,
    orm_tweets,
    tweets2medias,
    orm_users,
):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with session.begin():
        session.add_all(orm_users)
        session.flush()
        for models in (orm_tweets, orm_follows, orm_medias):
            session.add_all(models)
        session.flush()
        for like in likes:
            tweet: Tweet = orm_tweets[like.tweet_id]
            user: User = orm_users[like.user_id]
            tweet.likes.append(user)
        for tweet2media in tweets2medias:
            tweet: Tweet = orm_tweets[tweet2media.tweet_id]
            media: Media = orm_medias[tweet2media.media_id]
            tweet.media.append(media)
