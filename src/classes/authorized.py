from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Iterable

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from database import Session
from database import models as orm
from database import transaction
from database.funcs import download_images
from models import Like, TweetDump, TweetLoad, User, UserProfile

from . import exc, ext
from .abc import AuthorizedUserProtocol


class AuthorizedUser(AuthorizedUserProtocol):
    def __init__(self, orm_model: orm.User) -> None:
        self.__orm = orm_model

    @staticmethod
    @asynccontextmanager
    async def __get_user(user_id: int) -> AsyncGenerator[ext.UserContext, Any]:
        async with transaction() as session:
            if user := session.get(orm.User, user_id):
                yield ext.UserContext(session=session, orm=user)
            else:
                raise exc.UserDoesNotExist(f"User with id '{user_id}' not found")

    @staticmethod
    @asynccontextmanager
    async def __get_tweet(tweet_id: int) -> AsyncGenerator[ext.TweetContext, Any]:
        async with transaction() as session:
            if tweet := session.get(orm.User, tweet_id):
                yield ext.TweetContext(session=session, orm=tweet)
            else:
                raise exc.UserDoesNotExist(f"Tweet with id '{tweet_id}' not found")

    async def post_tweet(self, tweet: TweetLoad) -> int:
        async with transaction() as session:
            new = orm.Tweet(
                content=tweet.tweet_data,
                author_id=self.__orm.id,
                media=await download_images(tweet.tweet_media_ids),
            )
            session.add(new)
        return new.id

    async def add_image(self, image: bytes) -> int:
        async with transaction() as session:
            new = orm.Media(content=image, author_id=self.__orm.id)
            session.add(new)
        return new.id

    async def del_tweet(self, tweet_id: int) -> None:
        async with self.__get_tweet(tweet_id) as tweet:
            if tweet.orm.author_id == self.__orm.id:
                tweet.session.delete(tweet.orm)
            else:
                raise exc.NotOwnTweet("User cannot delete non it's own tweet")

    async def like(self, tweet_id: int) -> None:
        async with self.__get_tweet(tweet_id) as tweet:
            if tweet.orm not in self.__orm.likes:
                self.__orm.likes.append(tweet.orm)

    async def remove_like(self, tweet_id: int) -> None:
        async with self.__get_tweet(tweet_id) as tweet:
            if tweet.orm in self.__orm.likes:
                self.__orm.likes.remove(tweet.orm)

    async def follow(self, user_id: int) -> None:
        async with self.__get_user(user_id) as user:
            if await user.session.get(orm.Follow, (self.__orm.id, user_id)) is None:
                user.session.add(orm.Follow(follower_id=self.__orm.id, user_id=user_id))

    async def stop_following(self, user_id: int) -> None:
        async with self.__get_user(user_id) as user:
            if follow := await user.session.get(orm.Follow, (self.__orm.id, user_id)):
                user.session.delete(follow)

    async def generate_feed(self) -> list[TweetDump]:
        async with Session() as session:
            feed: Iterable[orm.Tweet] = await session.scalars(
                select(orm.Tweet)
                .join(orm.User)
                .join(orm.Follow)
                .filter_by(follower_id=self.__orm.id)
                .options(joinedload(orm.Tweet.likes, orm.Tweet.author))
                .order_by(orm.Tweet.creation_date.desc())
            )
            return [
                TweetDump(
                    id=tweet.id,
                    content=tweet.content,
                    attachments=[...],
                    author=User(id=tweet.author.id, name=tweet.author.name),
                    like=[
                        Like(user_id=user.id, name=user.name) for user in tweet.likes
                    ],
                )
                for tweet in feed
            ]

    async def check_profile(self) -> UserProfile:
        return self.check_user_profile(user_id=self.__orm.id)

    @classmethod
    async def check_user_profile(cls, user_id: int) -> UserProfile:
        async with cls.__get_user(user_id) as user:
            followers = await user.session.scalars(
                select(orm.User).join(orm.Follow).filter_by(follower_id=user_id)
            )
            follows = await user.session.scalars(
                select(orm.User).join(orm.Follow).filter_by(user_id=user_id)
            )
            return UserProfile(
                id=user_id,
                name=user.orm.name,
                followers=[User(id=user.id, name=user.name) for user in followers],
                following=[User(id=user.id, name=user.name) for user in follows],
            )
