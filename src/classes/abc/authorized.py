from typing import Protocol

from models import TweetDump, TweetLoad, UserProfile


class AuthorizedUserProtocol(Protocol):
    async def post_tweet(self, tweet: TweetLoad) -> int: ...

    async def add_image(self, image: bytes) -> int: ...

    async def del_tweet(self, tweet_id: int) -> None: ...

    async def like(self, tweet_id: int) -> None: ...

    async def remove_like(self, tweet_id: int) -> None: ...

    async def follow(self, user_id: int) -> None: ...

    async def stop_following(self, user_id: int) -> None: ...

    async def generate_feed(self) -> list[TweetDump]: ...

    async def check_profile(self) -> UserProfile: ...

    async def check_user_profile(cls, user_id: int) -> UserProfile: ...
