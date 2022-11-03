# PyCon PL 2022 - FastAPI + Redis


# How this project was initialized

1. Install poetry (https://python-poetry.org)
```
curl -sSL https://install.python-poetry.org | python3 -
```

2. Initialize the new project
```
poetry new pycon-fastapi
```

3. Add required dependencies

```
poetry add fastapi==0.85.1 aioredis==2.0.1 uvicorn==0.19.0 gunicorn==20.1.0
poetry add --dev pytest==7.1.3 mypy==0.982 flake8==5.0.4 black==22.10.0
```
