from pathlib import Path
from typing import TypeVar

import tomlkit
from pydantic import TypeAdapter

T = TypeVar("T")


def get_content(path: Path, type: type[T], *, default: T | None = None) -> T:
    parent = path.parent
    if not parent.exists():
        parent.mkdir(exist_ok=True)

    if not path.exists():
        if default is None:
            raise RuntimeError(f"{path} does not exist, and no default provided.")
        return default

    content = path.read_bytes()

    data = tomlkit.loads(content).unwrap()

    type_adapter = TypeAdapter(type)
    return type_adapter.validate_python(data)


def write_content(path: Path, type: type[T], inp: T):
    parent = path.parent
    if not parent.exists():
        parent.mkdir(exist_ok=True)

    type_adapter = TypeAdapter(type)
    data = type_adapter.dump_python(inp, mode="json")
    result = tomlkit.dumps(data).encode("utf-8")

    path.write_bytes(result)


def safe_path(name: str):
    return name.lower().replace(" ", "_").replace(":", "-")
