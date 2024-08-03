from typing import Annotated, TypeAlias

import cappa

from printed.cli.base import (
    PrintAdd,
    Printed,
    PrintList,
    PrintPrint,
    PrintRemove,
    console,
    state,
)
from printed.console import Console
from printed.formatting import format_cost
from printed.path import safe_path
from printed.schema import Link, Print, PrintMaterial, State

shape: TypeAlias = dict[str, Print]
PRINT_FILE = "settings.json"


def add_print(
    state: Annotated[State, cappa.Dep(state)],
    command: PrintAdd,
) -> Print:
    name = command.name or safe_path(command.title)
    if name in state.prints and not command.force:
        raise cappa.Exit(f"Print '{command.title}' already exists.")

    print_materials = []
    for cli_material in command.materials:
        cli_material_name, unit_count = cli_material.split("=")

        material = state.materials.get(cli_material_name)
        if not material:
            raise cappa.Exit(
                f"Invalid material '{cli_material_name}', existing materials include: {state.material_names}."
            )

        print_material = PrintMaterial(
            material=name,
            unit_count=int(unit_count),
            price_per_unit=material.price_per_unit,
        )
        print_materials.append(print_material)

    print = state.prints.add(
        Print(
            name=name,
            title=command.title,
            reference_cost=command.reference_cost,
            duration=command.duration,
            source_links=[Link(url=link) for link in command.source_links],
            reference_links=[Link(url=link) for link in command.reference_links],
            materials=print_materials,
        )
    )
    print.write()
    return print


def list_prints(
    state: Annotated[State, cappa.Dep(state)],
    console: Annotated[Console, cappa.Dep(console)],
    _: PrintList,
):
    columns = ["Name", "Count", "Total Cost"]
    table_result: list[tuple[str, ...]] = [
        (r.title, str(r.count), format_cost(r.total_printed_cost)) for r in state.prints
    ]

    console.table(
        "Prints",
        columns,
        table_result,
    )


def remove_print(
    state: Annotated[State, cappa.Dep(state)], printed: Printed, command: PrintRemove
):
    print = state.prints.get(command.name)

    if not print:
        print_names = ", ".join(p.name for p in state.prints)
        raise cappa.Exit(f"Print '{command.name}' not found from: {print_names}.")

    print.delete()
    print.write()


def print_print(state: Annotated[State, cappa.Dep(state)], command: PrintPrint):
    name = safe_path(command.name)

    print = state.prints.get(name)
    if not print:
        raise cappa.Exit(f"Invalid print {name}")

    print.append_history()
    print.write()
