from random import choice
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Media
from tests import faker

URL = "/api/medias"


@pytest.mark.asyncio
async def test_post_media(client: TestClient, users: list[dict], test_session: AsyncSession):
    filename = "test_img.jpg"
    path = f"./{filename}"
    user = choice(users)
    image = faker.image()
    
    with open(path, mode="wb") as file:
        file.write(image)
    
    response = client.post(URL, headers={"api-key": user["api_key"]}, files={"file": (filename, open(path, "rb"), "image/jpeg")})
    assert response.status_code == 200
    
    media = await test_session.get(Media, response.json()["media_id"])
    assert media.author_id == user["id"]
    assert media.content == image
    
    Path(path).unlink()
