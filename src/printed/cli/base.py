from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated

import cappa
from cappa.help import HelpFormatter
from dotenv import load_dotenv
from typing_extensions import Doc
from whenever import TimeDelta

from printed.console import Console
from printed.formatting import parse_duration
from printed.schema import State


def console(command: Printed):
    console = Console(command.verbose, force_terminal=command.tty)
    try:
        yield console
    except KeyboardInterrupt:
        console.show_cursor()
        raise cappa.Exit("Exiting...")


def state(command: Printed):
    return State.collect(command.path, read_materials=True)


@dataclass
class Printed:
    """A tool for tracking 3d print history."""

    command: cappa.Subcommands[Print | Material | Web | None] = None

    path: Annotated[
        Path,
        cappa.Arg(short=True, long=True, default=cappa.Env("PRINTED_PATH")),
        Doc("The location from which to organize a Printed print history."),
    ] = Path("./printed/")
    verbose: Annotated[
        int,
        cappa.Arg(short=True, long=True, action=cappa.ArgAction.count),
        Doc("Increase verbosity."),
    ] = 0
    tty: Annotated[bool | None, cappa.Arg(long="--tty/--no-tty")] = None

    def __call__(self):
        help_formatter = HelpFormatter()
        raise cappa.HelpExit(help_formatter(cappa.collect(Printed), "printed"))


@dataclass
class Print:
    command: cappa.Subcommands[PrintAdd | PrintRemove | PrintList | PrintPrint]


@cappa.command(name="add", invoke="printed.print.add_print")
@dataclass
class PrintAdd:
    title: str
    reference_cost: Annotated[float, cappa.Arg(short="-c", long=True)] = 0.0
    name: Annotated[str | None, cappa.Arg(short=True, long=True)] = None
    duration: Annotated[
        TimeDelta, cappa.Arg(short=True, long=True, parse=parse_duration)
    ] = field(default_factory=TimeDelta)
    source_links: Annotated[list[str], cappa.Arg(short=True, long="source-link")] = (
        field(default_factory=list)
    )
    reference_links: Annotated[
        list[str], cappa.Arg(short=True, long="reference-link")
    ] = field(default_factory=list)
    files: Annotated[list[Path], cappa.Arg(short=True, long=True)] = field(
        default_factory=list
    )
    materials: Annotated[list[str], cappa.Arg(short=True, long=True)] = field(
        default_factory=list
    )

    force: Annotated[bool, cappa.Arg(long=True)] = False


@cappa.command(name="remove", invoke="printed.print.remove_print")
@dataclass
class PrintRemove:
    name: str


@cappa.command(name="list", invoke="printed.print.list_prints")
@dataclass
class PrintList: ...


@cappa.command(name="print", invoke="printed.print.print_print")
@dataclass
class PrintPrint:
    name: str


@dataclass
class Material:
    command: cappa.Subcommands[MaterialAdd | MaterialRemove]


@cappa.command(name="add", invoke="printed.material.add")
class MaterialAdd:
    name: str
    unit: str
    price_per_unit: Annotated[float, cappa.Arg(short=True, long=True)] = 0.0


@cappa.command(name="remove", invoke="printed.material.remove")
class MaterialRemove:
    name: str


@dataclass
class Web:
    host: Annotated[str, cappa.Arg(long=True, default=cappa.Env("HOST"))] = "127.0.0.1"
    port: Annotated[
        int, cappa.Arg(short=True, long=True, default=cappa.Env("PORT"))
    ] = 8000
    root_path: Annotated[str, cappa.Arg(long=True, default=cappa.Env("ROOT_PATH"))] = ""

    def __call__(self, command: Printed):
        import uvicorn

        from printed.web.main import create_app

        uvicorn.run(
            create_app(command),
            host=self.host,
            port=self.port,
            root_path=self.root_path,
        )


def run():
    try:
        cappa.invoke(Printed, deps=[load_dotenv])
    except KeyboardInterrupt:
        sys.stderr.write("Exiting...\n")
