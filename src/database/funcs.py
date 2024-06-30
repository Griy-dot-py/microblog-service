from . import Session, models, transaction


async def upload_image(image: bytes) -> int:
    async with transaction() as session:
        new = models.Media(content=image)
        session.add(new)
    return new.id


async def download_images(ids: list[int]) -> list[models.Media]:
    images = []
    async with Session() as session:
        async for id in ids:
            if img := await session.get(models.Media, id):
                images.append(img)
    return images
