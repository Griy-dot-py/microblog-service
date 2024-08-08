from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from database import Session
from database import models as orm
from database import queries, transaction
from database.funcs import download_images
from models import Like, TweetDump, TweetLoad, User, UserProfile

from . import exc, ext
from .abc import AuthorizedUserProtocol


class AuthorizedUser(AuthorizedUserProtocol):
    def __init__(self, orm_model: orm.User) -> None:
        self.__orm = orm_model

    @staticmethod
    @asynccontextmanager
    async def __user_context(user_id: int) -> AsyncGenerator[ext.UserContext, Any]:
        async with transaction() as session:
            if user := await session.get(orm.User, user_id):
                yield ext.UserContext(session=session, user=user)
            else:
                raise exc.UserDoesNotExist(f"User with id '{user_id}' not found")

    @staticmethod
    @asynccontextmanager
    async def __tweet_context(tweet_id: int) -> AsyncGenerator[ext.TweetContext, Any]:
        async with transaction() as session:
            if tweet := await session.get(orm.Tweet, tweet_id):
                yield ext.TweetContext(session=session, tweet=tweet)
            else:
                raise exc.TweetDoesNotExist(f"Tweet with id '{tweet_id}' not found")

    async def post_tweet(self, tweet: TweetLoad) -> int:
        async with transaction() as session:
            new = orm.Tweet(
                content=tweet.tweet_data,
                author_id=self.__orm.id,
                media=await download_images(tweet.tweet_media_ids),
            )
            session.add(new)
            await session.flush()
            return new.id

    async def add_image(self, image: bytes) -> int:
        async with transaction() as session:
            new = orm.Media(content=image, author_id=self.__orm.id)
            session.add(new)
            await session.flush()
            return new.id

    async def del_tweet(self, tweet_id: int) -> None:
        async with self.__tweet_context(tweet_id) as context:
            if context.tweet.author_id == self.__orm.id:
                await context.session.delete(context.tweet)
            else:
                raise exc.NotOwnTweet("User cannot delete non it's own tweet")

    async def like(self, tweet_id: int) -> None:
        async with self.__tweet_context(tweet_id) as context:
            tweet_likes: list[orm.User] = await context.tweet.awaitable_attrs.likes
            ids = [user.id for user in tweet_likes]
            if self.__orm.id not in ids:
                tweet_likes.append(self.__orm)

    async def remove_like(self, tweet_id: int) -> None:
        async with self.__tweet_context(tweet_id) as context:
            tweet_likes: list[orm.User] = await context.tweet.awaitable_attrs.likes
            ids = [user.id for user in tweet_likes]
            if self.__orm.id in ids:
                like = ids.index(self.__orm.id)
                tweet_likes.pop(like)

    async def follow(self, user_id: int) -> None:
        async with self.__user_context(user_id) as context:
            if await context.session.get(orm.Follow, (self.__orm.id, user_id)) is None:
                context.session.add(orm.Follow(follower_id=self.__orm.id, user_id=user_id))

    async def stop_following(self, user_id: int) -> None:
        async with self.__user_context(user_id) as context:
            if follow := await context.session.get(orm.Follow, (self.__orm.id, user_id)):
                await context.session.delete(follow)

    async def generate_feed(self) -> list[TweetDump]:
        async with Session() as session:
            feed = await session.scalars(queries.feed(self.__orm))
            return [
                TweetDump(
                    id=tweet.id,
                    content=tweet.content,
                    attachments=[str(media.id) for media in tweet.media],
                    author=User(id=tweet.author.id, name=tweet.author.name),
                    like=[
                        Like(user_id=user.id, name=user.name) for user in tweet.likes
                    ],
                )
                for tweet in feed.unique()
            ]

    async def check_profile(self) -> UserProfile:
        return await self.check_user_profile(user_id=self.__orm.id)

    @classmethod
    async def check_user_profile(cls, user_id: int) -> UserProfile:
        async with cls.__user_context(user_id) as context:
            followers = await context.session.scalars(queries.followers(context.user))
            follows = await context.session.scalars(queries.follows(context.user))
            return UserProfile(
                id=user_id,
                name=context.user.name,
                followers=[User(id=user.id, name=user.name) for user in followers],
                following=[User(id=user.id, name=user.name) for user in follows],
            )

    @property
    def id(self) -> int:
        return self.__orm.id
