from typing import Tuple

from sqlalchemy import Select, select
from sqlalchemy.orm import aliased, joinedload

from .models import Follow, Tweet, User


def feed(for_user: User) -> Select[Tuple[Tweet]]:
    return (
        select(Tweet)
        .join(Follow, Follow.user_id == Tweet.author_id)
        .where(Follow.follower_id == for_user.id)
        .options(
            joinedload(Tweet.author, innerjoin=True),
            joinedload(Tweet.likes),
            joinedload(Tweet.media)
        )
        .order_by(Tweet.creation_date.desc())
    )

def tweet(id: int) -> Select[Tuple[Tweet]]:
    return (
        select(Tweet)
        .options(joinedload(Tweet.likes))
        .where(Tweet.id == id)
    )


def followers(user: User) -> Select[Tuple[User]]:
    follower = aliased(User)
    return (
        select(follower)
        .join(Follow, Follow.follower_id == follower.id)
        .where(Follow.user_id == user.id)
    )


def follows(user: User) -> Select[Tuple[User]]:
    author = aliased(User)
    return (
        select(author)
        .join(Follow, Follow.user_id == author.id)
        .where(Follow.follower_id == user.id)
    )


def user(api_key: str) -> Select[Tuple[User]]:
    return select(User).filter_by(api_key=api_key)
