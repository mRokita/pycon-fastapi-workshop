from enum import Enum

from starlette.config import Config


class AuthBackend(Enum):
    REDIS = "redis"
    MEMORY = "memory"


class ChatBackend(Enum):
    REDIS = "redis"
    MEMORY = "memory"


config = Config()

UVICORN_PORT: int = config("UVICORN_PORT", cast=int, default=8000)
UVICORN_HOST: str = config("UVICORN_HOST", cast=str, default="127.0.0.1")
PROXY_ROOT_PATH: str = config("PROXY_ROOT_PATH", cast=str, default="")
REDIS_URL: str = config("REDIS_URL", cast=str, default="redis://localhost")
CHAT_BACKEND: ChatBackend = config(  # type: ignore
    "CHAT_BACKEND", cast=ChatBackend, default="memory"
)
AUTH_BACKEND: AuthBackend = config(  # type: ignore
    "AUTH_BACKEND", cast=AuthBackend, default="memory"
)

if REDIS_URL and "decode_responses" not in REDIS_URL:
    url, *args = REDIS_URL.split("?", maxsplit=1)
    if args:
        args_str = "&"
    else:
        args_str = ""
    args_str += "decode_responses=true"
    REDIS_URL = url + "?" + args_str
