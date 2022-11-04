from __future__ import annotations

import asyncio
import secrets
from abc import ABC, abstractmethod
from typing import Dict

import aioredis

from pycon_chat.schemas import UserBase, User
from pycon_chat.settings import REDIS_URL


class AuthService(ABC):
    def close(self):  # noqa: B027
        pass

    @abstractmethod
    async def create_user(self, username: str, password: str) -> UserBase:
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    async def authenticate_user(self, username: str, password: str) -> UserBase:
        raise NotImplementedError  # pragma: nocover


class InvalidCredentials(Exception):
    ...


class MemoryAuthService(AuthService):
    _users: Dict[str, User] = {}

    async def authenticate_user(self, username: str, password: str) -> UserBase:
        user = self._users.get(username)
        if not user or not secrets.compare_digest(user.password, password):
            raise InvalidCredentials()
        return UserBase(**user.dict())

    async def create_user(self, username: str, password: str) -> UserBase:
        user = User(username=username, password=password)
        self._users[username] = user
        return UserBase(**user.dict())


class RedisAuthService(AuthService):
    def __init__(self) -> None:
        self.redis = aioredis.from_url(REDIS_URL)
        super().__init__()

    def close(self):
        asyncio.create_task(self.redis.close())
        asyncio.create_task(self.redis.connection_pool.disconnect())

    async def create_user(self, username: str, password: str) -> UserBase:
        await self.redis.hset(":users", mapping={username: password})
        return UserBase(username=username)

    async def authenticate_user(self, username: str, password: str) -> UserBase:
        db_password = await self.redis.hget(":users", username)
        if not db_password or not secrets.compare_digest(password, db_password):
            raise InvalidCredentials()
        return UserBase(username=username)
