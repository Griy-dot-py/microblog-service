from .result import Result
from .tweet_dump import TweetDump


class Feed(Result):
    tweets: list[TweetDump]
