import asyncio
from typing import (
    List,
    Optional,
)

from fastapi import FastAPI, Depends, Body, HTTPException, Path
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from pycon_chat.schemas import Channel, UserBase, User, MessageBase, Message
from pycon_chat.services.auth import (
    AuthService,
    InvalidCredentials,
    MemoryAuthService,
    RedisAuthService,
)
from pycon_chat.services.chat import ChatService, MemoryChatService, RedisChatService
from pycon_chat import __version__
from pycon_chat.settings import PROXY_ROOT_PATH, ChatBackend, AuthBackend

app = FastAPI(version=__version__, title="PyCon Chat API", root_path=PROXY_ROOT_PATH)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


class WebSocketBasicAuth(HTTPBasic):
    async def __call__(  # type: ignore
        self, request: Request = None, websocket: WebSocket = None
    ) -> Optional[HTTPBasicCredentials]:
        if not (bool(request) ^ bool(websocket)):
            raise RuntimeError(
                "Either request or websocket is required."
            )  # pragma: nocover
        if websocket:
            await websocket.accept()
            try:
                await self.websocket_handshake(websocket)
                return await super().__call__(websocket)  # type: ignore
            except HTTPException as e:
                await websocket.close(
                    code=status.WS_1008_POLICY_VIOLATION, reason=str(e.detail)
                )
        elif request:
            return await super().__call__(request)

    async def websocket_handshake(self, websocket: WebSocket):
        if "Authorization" not in websocket.headers:
            headers_copy = websocket.headers.mutablecopy()
            try:
                auth_message = await asyncio.wait_for(
                    websocket.receive_json(), timeout=10
                )
            except asyncio.TimeoutError:
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    detail="WS authentication timeout.",
                )
            else:
                headers_copy.setdefault(
                    "Authorization", auth_message.get("Authorization", "")
                )
                websocket._headers = headers_copy


auth = WebSocketBasicAuth()


def chat_service() -> ChatService:
    return app.state.chat_service


def auth_service() -> AuthService:
    return app.state.auth_service


@app.on_event("startup")
async def on_startup():
    from pycon_chat.settings import CHAT_BACKEND, AUTH_BACKEND

    app.state.chat_service = {
        ChatBackend.REDIS: RedisChatService,
        ChatBackend.MEMORY: MemoryChatService,
    }[CHAT_BACKEND]()

    app.state.auth_service = {
        AuthBackend.REDIS: RedisAuthService,
        AuthBackend.MEMORY: MemoryAuthService,
    }[AUTH_BACKEND]()


@app.on_event("shutdown")
async def on_shutdown():
    app.state.chat_service.close()
    app.state.auth_service.close()


async def authenticated_user(
    authentication: HTTPBasicCredentials = Depends(auth),
    auth: AuthService = Depends(auth_service),
) -> Optional[UserBase]:
    if not authentication:
        return None
    return await auth.authenticate_user(
        authentication.username, authentication.password
    )


@app.exception_handler(InvalidCredentials)
def handle_exception(request, exc):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Invalid credentials."},
    )


@app.get(
    "/channels",
    response_model=List[Channel],
    dependencies=[Depends(authenticated_user)],
)
async def list_channels(chat: ChatService = Depends(chat_service)):
    return await chat.get_channels()


async def channel_from_slug(
    channel_slug: str = Path(...), chat: ChatService = Depends(chat_service)
) -> Channel:
    channel = await chat.get_channel(channel_slug)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="channel not found"
        )
    return channel


@app.get("/channels/{channel_slug}/messages", response_model=List[Message])
async def list_channel_messages(
    channel: Channel = Depends(channel_from_slug),
    chat: ChatService = Depends(chat_service),
) -> List[Message]:
    return list(await chat.get_messages(channel.slug))


@app.post("/channels/{channel_slug}/messages", response_model=Message)
async def create_channel_message(
    user: UserBase = Depends(authenticated_user),
    channel: Channel = Depends(channel_from_slug),
    chat: ChatService = Depends(chat_service),
    message: MessageBase = Body(...),
) -> MessageBase:
    return await chat.send_message(channel.slug, user, message)


@app.post(
    "/channels", response_model=Channel, dependencies=[Depends(authenticated_user)]
)
async def create_channel(
    chat: ChatService = Depends(chat_service), channel: Channel = Body(...)
):
    return await chat.create_channel(slug=channel.slug, name=channel.name)


@app.websocket("/channels/{channel_slug}/messages_ws")
async def channel_messages_ws(
    websocket: WebSocket,
    chat: ChatService = Depends(chat_service),
    channel: Channel = Depends(channel_from_slug),
    user: Optional[UserBase] = Depends(authenticated_user),
):
    if not user:
        return
    async for message in chat.incoming_messages(
        channel_slug=channel.slug, read_timeout=1
    ):
        if message is ...:
            # No messages for some time, check if websocket is still active.
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
            except asyncio.TimeoutError:
                continue
            except WebSocketDisconnect:
                # Client disconnected
                break
            else:
                continue
        await websocket.send_json(jsonable_encoder(message.dict()))


@app.post("/users", response_model=UserBase, dependencies=[])
async def create_user(
    auth: AuthService = Depends(auth_service), user: User = Body(...)
) -> UserBase:
    return await auth.create_user(username=user.username, password=user.password)


@app.get("/users/me", response_model=UserBase)
def my_user(user: UserBase = Depends(authenticated_user)) -> UserBase:
    return user
