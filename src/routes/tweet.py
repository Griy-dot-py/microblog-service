from typing import Annotated

from fastapi import APIRouter, Header

from classes import MicroblogUser
from models import Feed, PostTweetDump, Result, TweetLoad

tweets = APIRouter(prefix="/tweets", tags=["tweet"])


@tweets.post("")
async def post_tweet(
    api_key: Annotated[str, Header()], tweet: TweetLoad
) -> PostTweetDump:
    async with MicroblogUser(api_key=api_key).authorize() as user:
        id = await user.post_tweet(tweet)
        return PostTweetDump(tweet_id=id)


@tweets.delete("/{id}")
async def delete_tweet(api_key: Annotated[str, Header()], id: int) -> Result:
    async with MicroblogUser(api_key=api_key).authorize() as user:
        await user.del_tweet(id)
        return Result()


@tweets.get("")
async def get_feed(api_key: Annotated[str, Header()]) -> Feed:
    async with MicroblogUser(api_key=api_key).authorize() as user:
        return Feed(tweets=await user.generate_feed())
