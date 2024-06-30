from typing import Annotated

from fastapi import APIRouter, File, Header

from classes import MicroblogUser
from models import MediaDump

medias = APIRouter(prefix="/medias")


@medias.post("")
async def post_media(
    api_key: Annotated[str, Header()], file: Annotated[bytes, File()]
) -> MediaDump:
    user = await MicroblogUser(api_key=api_key).authorize()
    id = await user.add_image(file)
    return MediaDump(media_id=id)
