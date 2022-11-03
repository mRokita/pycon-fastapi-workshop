import asyncio
from typing import TYPE_CHECKING

import aioredis.exceptions
import pytest
import pytest_asyncio
from aioredis import Redis
from starlette.config import environ

environ["REDIS_URL"] = "redis://localhost/13"

if TYPE_CHECKING:
    from pycon_chat.services.auth import (
        AuthService,
        MemoryAuthService,
        RedisAuthService,
    )
    from pycon_chat.services.chat import (
        ChatService,
        MemoryChatService,
        RedisChatService,
    )


@pytest_asyncio.fixture(autouse=True)
async def redis_connection():
    conn: Redis = Redis.from_url(
        "redis://localhost/13", decode_responses=True, encoding="utf-8"
    )
    try:
        await conn.flushdb()
    except aioredis.exceptions.ConnectionError:
        pass
    yield
    try:
        await conn.flushdb()
    except aioredis.exceptions.ConnectionError:
        pass
