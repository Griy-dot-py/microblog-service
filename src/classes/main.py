from sqlalchemy import select

from database import Session, transaction, models as orm
from database.funcs import download_images
from models import TweetLoad

from .abc import MicroblogUserProtocol


class MicroblogUser(MicroblogUserProtocol):
    def __init__(self, api_key: str):
        self.__api_key = api_key
    
    async def authorize(self) -> None:
        async with Session() as session:
            self.__orm = await session.scalar(
                select(orm.User).filter_by(api_key=self.__api_key)
            )
    
    @classmethod
    async def authorize_user(cls, api_key: str) -> "MicroblogUser":
        user = cls(api_key=api_key)
        await user.authorize()
        return user
    
    async def post_tweet(self, tweet: TweetLoad) -> None:
        async with transaction() as session:
            media = await download_images(tweet.tweet_media_ids)      
            session.add(
                orm.Tweet(content=tweet.tweet_data, author_id=self.__orm.id, media=media)
            )

    async def del_tweet(self, tweet_id: int) -> None:
        async with transaction() as session:
            tweet = await session.get(orm.Tweet, tweet_id)
            if tweet.author_id != self.__orm.id:
                raise ...
            session.delete(tweet)
    
    async def like(self, tweet_id: int) -> None:
        async with transaction() as session:
            tweet = await session.get(orm.Tweet, tweet_id)
            if tweet in self.__orm.likes:
                raise ...
            self.__orm.likes.append(tweet)
    
    async def remove_like(self, tweet_id: int) -> None:
        async with transaction() as session:
            tweet = await session.get(orm.Tweet, tweet_id)
            if tweet not in self.__orm.likes:
                raise ...
            self.__orm.likes.remove(tweet)
    
    async def follow(self, user_id: int) -> None:
        async with transaction() as session:
            if await session.get(orm.Follow, (self.__orm.id, user_id)):
                raise ...
            user = await session.get(orm.User, user_id)
            session.add(orm.Follow(follower_id=self.__orm.id, user_id=user_id))
    
    async def stop_following(self, user_id: int) -> None:
        async with transaction() as session:
            if not (follow := await session.get(orm.Follow, (self.__orm.id, user_id))):
                raise ...
            session.delete(follow)
    ...