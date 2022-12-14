from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from asyncio import Future
from types import EllipsisType
from typing import (
    Dict,
    Iterable,
    AsyncIterator,
    Tuple,
    List,
    Union,
    Optional,
)

import aioredis

from pycon_chat.schemas import Channel, MessageBase, Message, UserBase
from pycon_chat.settings import REDIS_URL


class ChatService(ABC):
    _channels: Dict[str, Channel]

    def close(self):  # noqa: B027
        pass

    @abstractmethod
    async def get_channels(self) -> Iterable[Channel]:
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    async def get_channel(self, slug: str) -> Optional[Channel]:
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    async def create_channel(self, slug: str, name: str) -> Channel:
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    async def get_messages(self, channel_slug: str) -> Iterable[Message]:
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    async def send_message(
        self,
        channel_slug: str,
        user: UserBase,
        message: MessageBase,
    ) -> Message:
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def incoming_messages(
        self, channel_slug: str, read_timeout: float = None, only_new: bool = False
    ) -> AsyncIterator[Union[Message, EllipsisType]]:
        raise NotImplementedError  # pragma: nocover


MessageSubscription = Future[Tuple[Message, "MessageSubscription"]]


class MemoryChatService(ChatService):
    _channels: Dict[str, Channel] = {}
    _messages: Dict[str, List[Message]] = {}
    _active_subscriptions: Dict[str, List[MessageSubscription]] = {}

    async def create_channel(self, slug: str, name: str) -> Channel:
        channel = Channel(slug=slug, name=name)
        self._channels[slug] = channel
        self._active_subscriptions[slug] = []
        self._messages[slug] = []
        return channel

    async def get_channel(self, slug: str) -> Optional[Channel]:
        return self._channels.get(slug)

    async def send_message(
        self, channel_slug: str, user: UserBase, message_base: MessageBase
    ) -> Message:
        message = Message(
            **message_base.dict(),
            sender_username=user.username,
            channel_slug=channel_slug,
        )
        self._messages[channel_slug].append(message)
        new_subscriptions: List[MessageSubscription] = []
        for future in self._active_subscriptions[channel_slug]:
            if future.cancelled():
                continue
            if future.done():
                raise RuntimeError("Done future in _active_subscriptions!")
            new_future: MessageSubscription = Future()
            new_subscriptions.append(new_future)
            future.set_result((message, new_future))
        self._active_subscriptions[channel_slug] = new_subscriptions
        return message

    async def get_channels(self) -> List[Channel]:
        return list(self._channels.values())

    async def get_messages(self, channel_slug) -> Iterable[Message]:
        return tuple(self._messages[channel_slug])

    async def incoming_messages(
        self, channel_slug: str, read_timeout: float = None, only_new: bool = False
    ) -> AsyncIterator[Union[Message, EllipsisType]]:
        future: MessageSubscription = Future()
        self._active_subscriptions[channel_slug].append(future)
        if not only_new:
            current_messages = await self.get_messages(channel_slug)
            for message in current_messages:
                yield message
        while True:
            try:
                result, future = await asyncio.wait_for(
                    asyncio.shield(future), timeout=read_timeout
                )
            except asyncio.TimeoutError:
                yield ...
            else:
                yield result


class RedisChatService(ChatService):
    def __init__(self):
        self.redis = aioredis.from_url(
            REDIS_URL, decode_responses=True, encoding="utf-8"
        )
        super().__init__()

    def close(self):
        asyncio.create_task(self.redis.close())
        asyncio.create_task(self.redis.connection_pool.disconnect())
