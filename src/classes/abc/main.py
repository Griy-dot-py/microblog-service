from typing import Protocol, AsyncGenerator, Any

from models import UserProfile

from .authorized import AuthorizedUserProtocol


class MicroblogUserProtocol(Protocol):
    def __init__(self, api_key: str) -> None: ...

    async def authorize(self) -> AsyncGenerator[AuthorizedUserProtocol, Any]: ...

    async def check_profile(cls, user_id: int) -> UserProfile: ...
