from typing import Protocol

from .authorized import AuthorizedUserProtocol


class MicroblogUserProtocol(Protocol):
    def __init__(self, api_key: str) -> None: ...

    async def authorize(self) -> "AuthorizedUserProtocol": ...
