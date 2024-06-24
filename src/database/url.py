import copy
from dataclasses import dataclass

PATTERN = "{dialect}+{driver}://{user}:{password}@{host}:{port}/{db}"


@dataclass
class SQLAlchemyURL:
    user: str
    password: str
    host: str
    db: str
    dialect: str = "postgresql"
    driver: str = "asyncpg"
    port: int = 5432

    def concatenate(self) -> str:
        return PATTERN.format(
            dialect=self.dialect,
            driver=self.driver,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            db=self.db,
        )

    def copy(self):
        return copy.deepcopy(self)
