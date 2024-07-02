from . import Session
from .models import Media


async def download_images(ids: list[int]) -> list[Media]:
    images = []
    async with Session() as session:
        for id in ids:
            if img := await session.get(Media, id):
                images.append(img)
    return images
