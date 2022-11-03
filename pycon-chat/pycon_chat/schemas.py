from __future__ import annotations

import datetime

import pydantic
from pydantic import Field


class Channel(pydantic.BaseModel):
    name: str = Field(min_length=1)
    slug: str = Field(min_length=1)

    class Config:
        allow_mutation = False


class UserBase(pydantic.BaseModel):
    username: str = Field(min_length=1)

    class Config:
        allow_mutation = False


class User(UserBase):
    password: str = Field(min_length=1)


class MessageBody(pydantic.BaseModel):
    text: str

    class Config:
        allow_mutation = False


class MessageBase(pydantic.BaseModel):
    body: MessageBody

    class Config:
        allow_mutation = False


class Message(MessageBase):
    sender_username: str
    channel_slug: str
    timestamp: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)
