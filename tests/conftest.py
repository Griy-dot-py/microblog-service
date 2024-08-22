import pytest
from config import settings

@pytest.fixture(scope="session", autouse=True)
def env():
    assert settings.TEST_MODE
