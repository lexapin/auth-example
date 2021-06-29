import asyncio
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from . import create_app
from .models import BaseModel, session_maker, engine


@pytest.fixture(scope="function", autouse=True)
async def fastapi_client():
    app = create_app(mode="TESTING")
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client


@pytest.fixture(scope="function", autouse=True)
async def database_session():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)

    try:
        async with session_maker() as session:
            yield session
    finally:
        pass


@pytest.yield_fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
