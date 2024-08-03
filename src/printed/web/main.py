import asyncio
import importlib.resources
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from watchfiles import awatch

from printed.cli.base import Printed
from printed.schema import State
from printed.web.routes import routes


def create_app(command: Printed, routes=routes):
    logging.basicConfig(level="INFO")

    app = FastAPI(command=command, lifespan=lifespan)

    static_dir = importlib.resources.files("printed.web.static")
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    for route in routes:
        app.add_api_route(
            path=route["path"],
            endpoint=route["endpoint"],
            methods=[route["method"]],
        )

    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    printed = app.extra["command"]

    app.extra["state"] = State.collect_all(printed.path)
    app.extra["watch_files"] = asyncio.create_task(watch_files(app, printed))
    yield


async def watch_files(app: FastAPI, printed: Printed):
    async for changes in awatch(printed.path):
        app.extra["state"] = State.collect_all(printed.path)
