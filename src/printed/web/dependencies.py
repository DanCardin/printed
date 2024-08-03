import functools
import importlib.resources
from collections.abc import Generator
from dataclasses import dataclass
from functools import cache
from typing import Annotated

from dataclass_settings import Env, load_settings
from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_303_SEE_OTHER

from printed.cli import base
from printed.formatting import (
    format_cost,
    format_datetime,
    format_duration,
    format_title,
    format_weight,
    relative_datetime,
)
from printed.schema import State


@dataclass(frozen=True)
class Config:
    timezone: Annotated[str, Env("TIMEZONE")] = "UTC"
    cost_symbol: Annotated[str, Env("COST_SYMBOL")] = "$"


@cache
def config():
    return load_settings(Config)


def printed(request: Request) -> base.Printed:
    return request.app.extra["command"]


def state(request: Request) -> State:
    return request.app.extra["state"]


def console(
    printed: Annotated[base.Printed, Depends(printed)],
) -> Generator[base.Console, None, None]:
    yield from base.console(printed)


@cache
def templates(config: Annotated[Config, Depends(config)]):
    template_dir = importlib.resources.files("printed.web").joinpath("templates")

    templates = Jinja2Templates(directory=str(template_dir))

    templates.env.filters["relative_datetime"] = relative_datetime
    templates.env.filters["format_datetime"] = functools.partial(
        format_datetime, timezone=config.timezone
    )
    templates.env.filters["duration"] = format_duration
    templates.env.filters["cost"] = functools.partial(
        format_cost, cost_symbol=config.cost_symbol
    )
    templates.env.filters["weight"] = format_weight
    templates.env.filters["title"] = format_title

    return templates


def get_template(request: Request, name: str) -> str:
    target = request.headers.get("HX-Target")
    if not target:
        return f"{name}.html"

    return f"{name}.{target}.html"


def redirect_to(request: Request, endpoint: str, **params):
    return RedirectResponse(
        url=request.url_for(endpoint, **params),
        status_code=HTTP_303_SEE_OTHER,
    )
