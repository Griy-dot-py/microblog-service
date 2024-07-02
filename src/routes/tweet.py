from typing import Annotated

from fastapi import APIRouter, Header

from classes import MicroblogUser
from models import Feed, PostTweetDump, Result, TweetLoad

tweets = APIRouter(prefix="/tweets", tags=["tweet"])


@tweets.post("")
async def post_tweet(
    api_key: Annotated[str, Header()], tweet: TweetLoad
) -> PostTweetDump:
    user = await MicroblogUser(api_key=api_key).authorize()
    id = await user.post_tweet(tweet)
    return PostTweetDump(tweet_id=id)


@tweets.delete("/{id}")
async def delete_tweet(api_key: Annotated[str, Header()], id: int) -> Result:
    user = await MicroblogUser(api_key=api_key).authorize()
    await user.del_tweet(id)
    return Result()


@tweets.get("")
async def get_feed(api_key: Annotated[str, Header()]) -> Feed:
    user = await MicroblogUser(api_key=api_key).authorize()
    return Feed(tweets=await user.generate_feed())
