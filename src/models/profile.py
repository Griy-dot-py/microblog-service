from .user import User


class UserProfile(User):
    followers: list[User]
    following: list[User]
