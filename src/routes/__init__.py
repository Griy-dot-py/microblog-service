from fastapi import APIRouter, FastAPI

from .media import medias
from .tweet import tweets
from .user import users

api = APIRouter(prefix="/api")
api.include_router(medias)
api.include_router(tweets)
api.include_router(users)

app = FastAPI()
app.include_router(api)
