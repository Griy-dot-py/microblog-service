from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from classes import exc
from models import Error
from database import dispose_after_all

from .follow import follow
from .like import likes
from .media import medias
from .tweet import tweets
from .user import users

api = APIRouter(prefix="/api")
api.include_router(follow)
api.include_router(likes)
api.include_router(medias)
api.include_router(tweets)
api.include_router(users)

app = FastAPI(lifespan=dispose_after_all)
app.include_router(api)


@app.exception_handler(exc.TweetDoesNotExist)
@app.exception_handler(exc.UserDoesNotExist)
def not_found_handler(
    request: Request, exc: exc.TweetDoesNotExist | exc.UserDoesNotExist
):
    raise HTTPException(404, exc.args)


@app.exception_handler(exc.NotOwnTweet)
def not_own_handler(request: Request, exc: exc.NotOwnTweet):
    msg, *_ = exc.args
    raise HTTPException(403, msg)


@app.exception_handler(Exception)
def server_exc_handler(request: Request, exc: Exception) -> Error:
    msg, *_ = exc.args
    return JSONResponse(
        Error(error_type=str(exc.__class__), error_message=msg).model_dump(), 500
    )
