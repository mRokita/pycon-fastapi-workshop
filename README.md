# Building scalable & efficient web applications with FastAPI, Redis and Docker
## PyCon PL 2022 workshop

The aim of this workshop is to introduce you to FastAPI, Redis and Docker.

After an introduction to these technologies (which will be mostly about FastAPI and Redis),
you will be introduced to a skeleton project (contained in this repository).  

We will work together to implement some features, that I have completely removed before the workshop.

I have also prepared a frontend client for the FastAPI application, so the workshop can be more interactive.

The target API specification is available [here](https://redocly.github.io/redoc/?url=https://gist.githubusercontent.com/mRokita/7e64f9960d1cae259b625662c68834b0/raw/77fbd64b2b61d9967c460645427c2f66ba81000c/openapi.yaml#tag/store_model).

This project also contains a pytest suite which covered 95% of the original source code,
including a websocket which can't be included in the OpenAPI specification.

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
Open http://localhost:8081/ in your browser and make sure that value of the "API URL" text field is green (see the picture attached).
Don't worry if the app does not work - most backend features have been removed on purpose.

![](https://i.imgur.com/uOwetJ8.png)

You can run tests with `docker compose exec backend pytest`. 
Don't worry if most of them fail - during the workshop it will be our job to make them pass.

## Without Docker (not required, but recommended for running tests)

You will need Python 3.7+, although 3.10 is recommended and is the only version that I've tested.

Poetry is required to install project dependencies (https://python-poetry.org/docs/#installation).  
By default, Poetry automatically creates a virtualenv, so it is enough to run the following commands:

```
# Commands relative to project root
cd pycon-chat
poetry install
poetry run python -m pycon_chat
```

If you want to run the frontend, which is based on the [Svelte](https://svelte.dev/) framework, 
the only thing that you need is [npm](https://www.npmjs.com/).  
To install all the dependencies, you just need to run the following commands:

```
# Commands relative to project root
cd frontend
npm install
npm run dev
```

Make sure that both frontend & backend servers are running.  
Open frontend in your browser, and make sure that value of the "API URL" text field is green (see the picture attached).

![](https://i.imgur.com/5iQcYcG.png)

To run tests, execute `make test` from the `pycon-chat` directory.