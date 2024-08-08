from itertools import permutations
from random import choice, random

from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import settings
from tests import faker, Like, Tweet2Media
from database.models import Base, Follow, Media, Tweet, User
from models import TweetLoad


@fixture
def eng():
    url = "postgresql+psycopg2://{user}:{passw}@{host}:5432/{db}".format(
        user=settings.POSTGRES_USER,
        passw=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        db=settings.POSTGRES_DB,
    )
    engine = create_engine(url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


# @fixture(autouse=True)
# def session(
#     eng,
#     orm_users,
#     orm_follows,
#     orm_tweets,
#     likes,
#     orm_medias,
#     tweets2medias,
# ):
#     Base.metadata.drop_all(eng)
#     Base.metadata.create_all(eng)
    
#     with Session(bind=eng) as session:
#         with session.begin():
#             session.add_all(orm_users)
#             session.flush()
#             for models in (orm_follows, orm_tweets, orm_medias):
#                 session.add_all(models)
#             session.flush()
            

@fixture
def orm_users(eng):
    keys = [faker.password(length=12) for _ in range(3)]
    assert len(keys) == len({*keys})
    users = [User(api_key=key, name=faker.name()) for key in keys]
    with Session(bind=eng) as session:
        with session.begin():
            session.add_all(users)
        assert users[0].id is not None
        yield users


@fixture
def orm_follows(eng, orm_users: list[User]):
    follow_set = {*permutations(orm_users, 2)}
    follows = []
    for _ in range(3):
        follower, user = follow_set.pop()
        follows.append(Follow(follower_id=follower.id, user_id=user.id))
    with Session(bind=eng) as session:
        with session.begin():
            session.add_all(follows)
        yield follows


@fixture
def orm_tweets(eng, orm_users: list[User]):
    tweets = [
        Tweet(
            content=faker.text(),
            author_id=choice(orm_users).id,
            creation_date=faker.date_time()
        ) for _ in range(7)
    ]
    with Session(bind=eng) as session:
        with session.begin():
            session.add_all(tweets)
        yield tweets


@fixture
def likes(eng, orm_users: list[User], orm_tweets: list[Tweet]):
    id_list = []
    while len(id_list) < 3:
        ids = (choice(orm_users).id, choice(orm_tweets).id)
        if ids not in id_list:
            id_list.append(ids)
    likes = [Like(user_id=user_id, tweet_id=tweet_id) for user_id, tweet_id in id_list]
    with Session(bind=eng) as session:
        with session.begin():
            for like in likes:
                tweet = orm_tweets[like.tweet_id - 1]
                user = orm_users[like.user_id - 1]
                tweet.likes.append(user)
        yield likes

@fixture
def orm_medias(eng, orm_users: list[User]):
    medias = [Media(content=faker.image(), author_id=choice(orm_users).id) for _ in range(3)]
    with Session(bind=eng) as session:
        with session.begin():
            session.add_all(medias)
        yield medias


@fixture
def tweets2medias(eng, session: Session, orm_tweets: list[Tweet], orm_medias: list[Media]):
    id_list = []
    while len(id_list) < 5:
        ids = (choice(orm_tweets).id, choice(orm_medias).id)
        if ids not in id_list:
            id_list.append(ids)
    ts2ms = [Tweet2Media(tweet_id=tweet_id, media_id=media_id) for tweet_id, media_id in id_list]
    with Session(bind=eng) as session:
        with session.begin():
            for t2m in ts2ms:
                tweet = orm_tweets[t2m.tweet_id - 1]
                media = orm_medias[t2m.media_id - 1]
                tweet.media.append(media)
        yield ts2ms


@fixture
def tweet_load(orm_medias: list[Media]):
    media_ids = {media.id for media in orm_medias}
    added = []
    for _ in range(2):
        if random() < 5:
            added.append(media_ids.pop())
    return TweetLoad(tweet_data=faker.text(), tweet_media_ids=added)
