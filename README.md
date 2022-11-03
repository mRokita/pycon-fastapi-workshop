# Building scalable & efficient web applications with FastAPI, Redis and Docker
## PyCon PL 2022 workshop

# !BEFORE THE WORKSHOP! Configuration

## Docker

First, you need to install the tools required, which are Docker and Docker Compose.
If you don't have them already, please install them before the workshop

- [Docker Engine installation overview](https://docs.docker.com/engine/install/)
- [Docker Compose plugin installation](https://docs.docker.com/compose/install/linux/)

After installing Docker, please clone this repo:

```
git clone https://github.com/mRokita/pycon-fastapi-workshop
cd pycon-fastapi-workshop
```

After cloning the repo, test if everything works by running `sudo docker compose up --build`.
Open http://localhost:8081/ in your browser and make sure that text inside of the "API URL" text field is green (see the picture attached).

![](https://i.imgur.com/uOwetJ8.png)