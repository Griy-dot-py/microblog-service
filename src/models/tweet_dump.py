from pydantic import BaseModel

from .user import User
from .like import Like

class TweetDump(BaseModel):
    id: int
    content: str
    attachments: list[str]
    author: User
    like: list[Like]
