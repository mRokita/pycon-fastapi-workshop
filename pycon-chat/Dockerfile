FROM python:3.10-slim

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME=/usr \
    POETRY_CHECKSUM=e4fcc31fc7cc159fe350c0e9bfceac9755f6bcfe5288d11e740a2345e6866562c5f43da6243f982f05e24f1e0f3a6cb911e71e45e3b6f2d76e658b1f7c61c38c
WORKDIR /app

ADD https://raw.githubusercontent.com/python-poetry/poetry/b47de09/install-poetry.py install-poetry.py
RUN echo "${POETRY_CHECKSUM}  install-poetry.py" | sha512sum --check

RUN python install-poetry.py

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi
COPY pycon_chat /app/pycon_chat
COPY tests /app/tests
RUN poetry install --no-interaction --no-ansi
LABEL maintainer="Michał Rokita <mrokita@mrokita.pl>"
EXPOSE 80
ENV UVICORN_PORT=80 \
    UVICORN_HOST=0.0.0.0
ENTRYPOINT python -m pycon_chat
# In production you should use:
#   CMD gunicorn pycon_chat.web:app --reload -k uvicorn.workers.UvicornWorker -b 0.0.0.0:80
