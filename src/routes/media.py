from typing import Annotated

from fastapi import APIRouter, Header, UploadFile

from classes import MicroblogUser
from models import MediaDump

medias = APIRouter(prefix="/medias", tags=["media"])


@medias.post("")
async def post_media(
    api_key: Annotated[str, Header()], file: UploadFile
) -> MediaDump:
    user = await MicroblogUser(api_key=api_key).authorize()
    data = await file.read()
    id = await user.add_image(data)
    return MediaDump(media_id=id)
