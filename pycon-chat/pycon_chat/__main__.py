import uvicorn
from pycon_chat.settings import UVICORN_PORT, UVICORN_HOST


def main():
    uvicorn.run(
        "pycon_chat.web:app", reload=True, port=UVICORN_PORT, host=UVICORN_HOST
    )  # pragma: nocover


if __name__ == "__main__":
    main()  # pragma: nocover
