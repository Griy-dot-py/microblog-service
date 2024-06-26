from pydantic import BaseModel


class TweetLoad(BaseModel):
    tweet_data: str
    tweet_media_ids: list[int]
