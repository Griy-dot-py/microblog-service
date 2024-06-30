from . import Session, models


async def download_images(ids: list[int]) -> list[models.Media]:
    images = []
    async with Session() as session:
        async for id in ids:
            if img := await session.get(models.Media, id):
                images.append(img)
    return images
