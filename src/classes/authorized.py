from sqlalchemy.ext.asyncio import AsyncSession

from database import Session
from database import models as orm
from database import queries
from database.funcs import download_images
from models import Like, TweetDump, TweetLoad, User, UserProfile

from . import exc
from .abc import AuthorizedUserProtocol


class AuthorizedUser(AuthorizedUserProtocol):
    def __init__(self, orm_model: orm.User, session: AsyncSession) -> None:
        self.__orm = orm_model
        self.__session = session

    @property
    def id(self) -> int:
        return self.__orm.id

    @property
    def name(self) -> str:
        return self.__orm.name

    async def __get_user(self, user_id: int) -> orm.User:
        if user := await self.__session.get(orm.User, user_id):
            return user
        else:
            raise exc.UserDoesNotExist(f"User with id '{user_id}' not found")

    async def __get_tweet(self, tweet_id: int) -> orm.Tweet:
        if tweet := await self.__session.scalar(queries.tweet(tweet_id)):
            return tweet
        else:
            raise exc.TweetDoesNotExist(f"Tweet with id '{tweet_id}' not found")

    async def post_tweet(self, tweet: TweetLoad) -> int:
        new = orm.Tweet(
            content=tweet.tweet_data,
            author_id=self.id,
            media=await download_images(self.__session, tweet.tweet_media_ids),
        )
        self.__session.add(new)
        await self.__session.flush()
        return new.id

    async def add_image(self, image: bytes) -> int:
        new = orm.Media(content=image, author_id=self.__orm.id)
        self.__session.add(new)
        await self.__session.flush()
        return new.id

    async def del_tweet(self, tweet_id: int) -> None:
        tweet = await self.__get_tweet(tweet_id)
        if tweet.author_id == self.__orm.id:
            await self.__session.delete(tweet)
            await self.__session.flush()
        else:
            raise exc.NotOwnTweet("User cannot delete non it's own tweet")

    async def like(self, tweet_id: int) -> None:
        tweet = await self.__get_tweet(tweet_id)
        if self.__orm.id not in {u.id for u in tweet.likes}:
            tweet.likes.append(self.__orm)
            await self.__session.flush()

    async def remove_like(self, tweet_id: int) -> None:
        tweet = await self.__get_tweet(tweet_id)
        ids = [u.id for u in tweet.likes]
        if self.__orm.id in ids:
            tweet.likes.pop(ids.index(self.__orm.id))
            await self.__session.flush()

    async def follow(self, user_id: int) -> None:
        await self.__get_user(user_id)
        if await self.__session.get(orm.Follow, (self.__orm.id, user_id)) is None:
            self.__session.add(orm.Follow(follower_id=self.__orm.id, user_id=user_id))
            await self.__session.flush()

    async def stop_following(self, user_id: int) -> None:
        await self.__get_user(user_id)
        if follow := await self.__session.get(orm.Follow, (self.__orm.id, user_id)):
            await self.__session.delete(follow)
            await self.__session.flush()

    async def generate_feed(self) -> list[TweetDump]:
        feed = await self.__session.scalars(queries.feed(self.__orm))
        return [
            TweetDump(
                id=tweet.id,
                content=tweet.content,
                attachments=[str(media.id) for media in tweet.media],
                author=User(id=tweet.author.id, name=tweet.author.name),
                like=[Like(user_id=user.id, name=user.name) for user in tweet.likes],
            )
            for tweet in feed.unique()
        ]

    async def check_profile(self) -> UserProfile:
        followers = await self.__session.scalars(queries.followers(self.__orm))
        follows = await self.__session.scalars(queries.follows(self.__orm))
        return UserProfile(
            id=self.id,
            name=self.__orm.name,
            followers=[User(id=user.id, name=user.name) for user in followers],
            following=[User(id=user.id, name=user.name) for user in follows],
        )

    @classmethod
    async def check_user_profile(cls, user_id: int) -> UserProfile:
        async with Session() as session:
            user = cls(session=session, orm_model=orm.User())
            user.__orm = await user.__get_user(user_id)
            return await user.check_profile()
