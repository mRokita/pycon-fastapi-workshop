from fastapi import FastAPI, Depends
from fastapi.security import HTTPBasic
from pycon_chat.schemas import User, UserBase
from starlette.middleware.cors import CORSMiddleware
from pycon_chat.services.auth import (
    AuthService,
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

auth = HTTPBasic()


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


@app.post("/users", response_model=UserBase)
async def create_user(user: User, auth_backend: AuthService = Depends(auth_service)):
    return await auth_backend.create_user(user.username, user.password)
