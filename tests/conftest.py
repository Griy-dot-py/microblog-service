from pytest import fixture

ENV_PATH = "config/.env"
TEST_ENV_PATH = "config/.env.test"

with open(ENV_PATH) as f:
    old = f.read()
with open(TEST_ENV_PATH) as f:
    new = f.read()
with open(ENV_PATH, "w") as f:
    f.write(new)
print("ENV MOCK COMPLETE!")


@fixture(scope="session", autouse=True)
def env():
    yield
    
    with open (ENV_PATH, "w") as f:
        f.write(old)
