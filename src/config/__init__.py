from dotenv import find_dotenv, load_dotenv

if not find_dotenv():
    exit("Cannot load environment variables. There's no .env file")
else:
    load_dotenv()

from . import postgres

__all__ = [postgres]
