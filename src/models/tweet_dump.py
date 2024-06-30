from pydantic import BaseModel

from .like import Like
from .user import User


class TweetDump(BaseModel):
    id: int
    content: str
    attachments: list[str]
    author: User
    like: list[Like]
