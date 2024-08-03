from collections.abc import Callable
from typing import Literal, TypedDict

from printed.web import prints


class Route(TypedDict):
    path: str
    endpoint: Callable
    method: Literal["POST", "GET", "DELETE", "PUT"]


routes: list[Route] = [
    {
        "method": "GET",
        "path": "/",
        "endpoint": prints.render("index"),
    },
    {
        "method": "GET",
        "path": "/material",
        "endpoint": prints.render("material"),
    },
    {
        "method": "GET",
        "path": "/print/{name}",
        "endpoint": prints.render("print"),
    },
    {
        "method": "POST",
        "path": "/print",
        "endpoint": prints.add_print,
    },
    {
        "method": "PUT",
        "path": "/print/{name}",
        "endpoint": prints.update_print,
    },
    {
        "method": "DELETE",
        "path": "/print/{name}",
        "endpoint": prints.delete_print,
    },
    {
        "method": "POST",
        "path": "/print/{name}/history",
        "endpoint": prints.append_history,
    },
    {
        "method": "DELETE",
        "path": "/print/{name}/history/{number}",
        "endpoint": prints.delete_history,
    },
    {
        "method": "POST",
        "path": "/print/{name}/source_link",
        "endpoint": prints.append_source_link,
    },
    {
        "method": "DELETE",
        "path": "/print/{name}/source_link/{number}",
        "endpoint": prints.delete_source_link,
    },
]
