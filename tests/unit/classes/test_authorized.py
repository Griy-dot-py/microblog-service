from pytest import fixture, mark, raises

from classes import AuthorizedUser
from classes.exc import UserDoesNotExist


@fixture
def instance(orm_users):
    first, *_ = orm_users
    return AuthorizedUser(orm_model=first)


@mark.asyncio_cooperative
async def test__user_context(instance, orm_users):
    user = orm_users[-1]
    async with instance._AuthorizedUser__user_context(user.id) as context:
        name = context.user.name
    assert user.name == name


@mark.asyncio_cooperative
async def test__user_context_raises(instance, orm_users):
    unexitsting_id = len(orm_users)
    with raises(UserDoesNotExist):
        async with instance._AuthorizedUser__user_context(unexitsting_id):
            pass
