import pytest
import pytest_asyncio
from aioredis import Redis

from pycon_chat.services.auth import (
    AuthService,
    InvalidCredentials,
    MemoryAuthService,
    RedisAuthService,
)
from pycon_chat.services.chat import ChatService, MemoryChatService, RedisChatService


@pytest.fixture(params=[MemoryAuthService, RedisAuthService])
def auth_service(request, redis_connection) -> AuthService:
    return request.param()


@pytest.fixture(params=[MemoryChatService, RedisChatService])
def chat_service(request, redis_connection) -> ChatService:
    return request.param()


@pytest.mark.asyncio
async def test_auth_service(auth_service):
    with pytest.raises(InvalidCredentials):
        await auth_service.authenticate_user("none", "none")
    await auth_service.create_user("testlogin", "testpassword")
    assert (
        await auth_service.authenticate_user("testlogin", "testpassword")
    ).dict() == {"username": "testlogin"}
