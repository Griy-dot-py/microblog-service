from pydantic import BaseModel


class MediaDump(BaseModel):
    result: bool = True
    media_id: int
