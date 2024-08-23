from sqlalchemy.ext.asyncio import AsyncSession

from .models import Media


async def download_images(session: AsyncSession, ids: list[int]) -> list[Media]:
    images = []
    for id in ids:
        if img := await session.get(Media, id):
            images.append(img)
    return images
