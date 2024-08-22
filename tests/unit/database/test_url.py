import pytest
from random import choice

from database import SQLAlchemyURL
from tests import faker

PATTERN = "{dialect}+{driver}://{user}:{password}@{host}:{port}/{db}"
DIALECTS = ("postgresql", "sqlite", "mysql")
DRIVERS = ("asyncpg", "psycopg2")

@pytest.fixture
def settings():
    return dict(
        user=faker.first_name(),
        password=faker.password(length=10),
        host=faker.ipv4(),
        db=faker.word(),
        dialect=choice(DIALECTS),
        driver=choice(DRIVERS),
        port=faker.port_number()
    )

def test_concatenate(settings: dict):
    url = SQLAlchemyURL(**settings).concatenate()
    assert url == PATTERN.format(**settings)

def test_copy(settings: dict):
    origin = SQLAlchemyURL(**settings)
    copied = origin.copy()
    
    assert copied is not origin
    assert copied.user == origin.user
    assert copied.password == origin.password
    assert copied.host == origin.host
    assert copied.db == origin.db
    assert copied.dialect == origin.dialect
    assert copied.driver == origin.driver
    assert copied.port == origin.port

    copied.password = faker.password(length=30)
    assert copied.password != origin.password
