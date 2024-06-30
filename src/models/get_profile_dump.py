from .profile import UserProfile
from .result import Result


class GetProfileDump(Result):
    user: UserProfile
