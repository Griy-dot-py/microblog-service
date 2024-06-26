from . import transaction, Session
from . import models


async def upload_images(images: list[bytes]) -> list[int]:
    ids = []
    async with transaction() as session:
        async for image in images:
            new = models.Media(content=image)
            session.add(new)
            await session.flush()
            ids.append(new.id)
    return ids


async def download_images(ids: list[int]) -> list[models.Media]:
    images = []
    async with Session() as session:
        async for id in ids:
            if img := await session.get(models.Media, id):
                images.append(img)
    return images
