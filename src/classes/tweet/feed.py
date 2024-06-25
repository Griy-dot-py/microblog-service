from typing import TypeVar
from . posted import PostedTweet


Feed = TypeVar("Feed", list[PostedTweet])
