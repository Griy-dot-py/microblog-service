from pydantic import BaseModel


class PostTweetDump(BaseModel):
    result: bool = True
    tweet_id: int
