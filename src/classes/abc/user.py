from typing import Protocol
from ..tweet import TweetDraft, Feed
from ..user_data import UserData


class MicroblogUserProtocol(Protocol):
    def __init__(self, api_key: str) -> None: ...
    
    def post_tweet(self, tweet: TweetDraft) -> None: ...
    
    def del_tweet(self, tweet_id: int) -> None: ...
    
    def like(self, tweet_id: int) -> None: ...
    
    def remove_like(self, tweet_id: int) -> None: ...
    
    def follow(self, user_id: int) -> None: ...
    
    def stop_following(self, user_id: int) -> None: ...
    
    def generate_feed(self) -> Feed: ...
    
    @property
    def followers(self) -> list[UserData]: ...
    
    @property
    def follows(self) -> list[UserData]: ...
