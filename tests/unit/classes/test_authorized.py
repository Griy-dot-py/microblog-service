from pytest import fixture

from classes import AuthorizedUser


@fixture
def instance(orm_users):
    model, *_ = orm_users
    return AuthorizedUser(orm_model=model)


