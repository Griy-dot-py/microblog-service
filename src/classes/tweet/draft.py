from dataclasses import dataclass


@dataclass
class TweetDraft:
    content: str
    media_ids: list[int] | None = None
