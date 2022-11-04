from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from pycon_chat.schemas import User, UserBase
from starlette.middleware.cors import CORSMiddleware
from pycon_chat.services.auth import (
    AuthService,
    MemoryAuthService,
    RedisAuthService, InvalidCredentials,
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


@app.exception_handler(InvalidCredentials)
def handle_invalid_credentials(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Invalid credentials."},
    )


@app.get("/users/me", response_model=UserBase)
async def my_user(credentials: HTTPBasicCredentials = Depends(auth),
                  auth_backend: AuthService = Depends(auth_service)):
    user: UserBase = await auth_backend.authenticate_user(
        credentials.username,
        credentials.password)
    print("password: ", credentials.password)
    return user