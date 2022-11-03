import asyncio
from base64 import b64encode

import pytest
import pytest_asyncio
from async_asgi_testclient import TestClient
from starlette import status
from starlette.config import environ
from starlette.websockets import WebSocket

from pycon_chat import settings
from pycon_chat.schemas import Channel, MessageBase, MessageBody, UserBase
from pycon_chat.services.auth import AuthService, MemoryAuthService
from pycon_chat.services.chat import ChatService, MemoryChatService
from pycon_chat.settings import AuthBackend, ChatBackend
from pycon_chat.web import app


def get_client():
    return TestClient(app)


@pytest.fixture(params=[ChatBackend.REDIS, ChatBackend.MEMORY])
def chat_backend(request):
    settings.CHAT_BACKEND = request.param


@pytest.fixture(params=[AuthBackend.REDIS, AuthBackend.MEMORY])
def auth_backend(request):
    settings.CHAT_BACKEND = request.param


@pytest_asyncio.fixture
def auth_service(client):
    return app.state.auth_service


@pytest_asyncio.fixture
def chat_service(client):
    return app.state.chat_service


@pytest_asyncio.fixture
async def client(auth_backend, chat_backend):
    async with get_client() as client:
        yield client


@pytest_asyncio.fixture
async def channel(chat_service: ChatService) -> Channel:
    return await chat_service.create_channel(name="test", slug="testslug")


@pytest_asyncio.fixture
async def authenticated_client(auth_service: AuthService) -> TestClient:
    await auth_service.create_user("test", "password")
    async with get_client() as client:
        client.headers.update(
            {"Authorization": f"Basic {b64encode(b'test:password').decode('ascii')}"}
        )
        yield client


@pytest.mark.asyncio
async def test_create_user(client):
    res = await client.post("/users", json={"username": "test2", "password": "test2"})
    assert res.status_code == status.HTTP_200_OK, res.text
    assert res.json() == {"username": "test2"}


@pytest.mark.asyncio
async def test_create_channel(client, authenticated_client):
    res = await client.post("/channels", json={"slug": "test", "name": "test"})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED, res.text
    res = await authenticated_client.post(
        "/channels", json={"slug": "test", "name": "test"}
    )
    assert res.status_code == status.HTTP_200_OK, res.text
    assert res.json() == {"slug": "test", "name": "test"}
    res = await client.get("/channels")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED, res.text
    res = await authenticated_client.get("/channels")
    assert res.status_code == status.HTTP_200_OK, res.text
    assert res.json() == [{"name": "test", "slug": "test"}]


@pytest.mark.asyncio
async def test_my_user(authenticated_client: TestClient):
    res = await authenticated_client.get("/users/me")
    assert res.status_code == status.HTTP_200_OK, res.text
    assert res.json() == {"username": "test"}
    authenticated_client.headers.update({"Authorization": "Basic YTpi"})
    res = await authenticated_client.get("/users/me")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED, res.text
    assert res.json() == {"detail": "Invalid credentials."}


@pytest.mark.asyncio
async def test_ws(authenticated_client, channel, chat_service: ChatService):
    await chat_service.send_message(
        channel.slug,
        UserBase(username="test"),
        MessageBase(body=MessageBody(text="test")),
    )
    async with authenticated_client.websocket_connect(
        f"/channels/{channel.slug}/messages_ws"
    ) as ws:
        await ws.send_json(
            {"Authorization": authenticated_client.headers.get("Authorization")}
        )
        ws: WebSocket
        msg = await ws.receive_json()
        msg.pop("timestamp")
        assert msg == {
            "body": {"text": "test"},
            "channel_slug": "testslug",
            "sender_username": "test",
        }
        await asyncio.sleep(1)  # to cover timeouts
        await chat_service.send_message(
            channel.slug,
            UserBase(username="test"),
            MessageBase(body=MessageBody(text="test2")),
        )
        msg = await ws.receive_json()
        msg.pop("timestamp")
        assert msg == {
            "body": {"text": "test2"},
            "channel_slug": "testslug",
            "sender_username": "test",
        }


@pytest.mark.asyncio
async def test_ws_auth(client, channel):
    async with client.websocket_connect(f"/channels/{channel.slug}/messages_ws") as ws:
        ws: WebSocket
        with pytest.raises(Exception) as e:
            await ws.send_json({"Authorization": "abc"})
            await ws.receive_json()
        assert e.value.args == (
            {"code": 1008, "reason": "Not authenticated", "type": "websocket.close"},
        )


@pytest.mark.asyncio
async def test_messages(authenticated_client, channel):
    res = await authenticated_client.get(f"/channels/invalidchan/messages")
    assert res.status_code == status.HTTP_404_NOT_FOUND, res.text
    res = await authenticated_client.get(f"/channels/{channel.slug}/messages")
    assert res.status_code == status.HTTP_200_OK, res.text
    assert res.json() == []
    res = await authenticated_client.post(
        f"/channels/{channel.slug}/messages",
        json=MessageBase(body=MessageBody(text="test")).dict(),
    )
    assert res.status_code == status.HTTP_200_OK, res.text
    data = res.json()
    data.pop("timestamp")
    assert data == {
        "body": {"text": "test"},
        "channel_slug": "testslug",
        "sender_username": "test",
    }

    res = await authenticated_client.get(f"/channels/{channel.slug}/messages")
    assert res.status_code == status.HTTP_200_OK, res.text
    data = res.json()
    for c in data:
        c.pop("timestamp")
    assert data == [
        {
            "body": {"text": "test"},
            "channel_slug": "testslug",
            "sender_username": "test",
        }
    ]
