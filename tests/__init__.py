from collections import namedtuple

from faker import Faker

faker = Faker()
Like = namedtuple("Like", ("user_id", "tweet_id"))
Tweet2Media = namedtuple("Tweet2Media", ("tweet_id", "media_id"))
