from dataclasses import dataclass
from .draft import TweetDraft
from classes.user_data import UserData


@dataclass
class PostedTweet(TweetDraft):
    id: int
    likes: list[UserData]
    author: UserData
