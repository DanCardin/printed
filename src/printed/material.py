from typing import TypeAlias

import cappa

from printed.cli.base import MaterialAdd, MaterialRemove, Printed
from printed.schema import Material, State

shape: TypeAlias = dict[str, Material]


def add(printed: Printed, command: MaterialAdd):
    state = State.collect(printed.path, read_materials=True)

    if command.name in state.materials:
        raise cappa.Exit(f"Material '{command.name}' already exists.")

    state.materials[command.name] = Material(
        name=command.name,
        unit=command.unit,
        price_per_unit=command.price_per_unit,
    )

    state.write_materials()


def remove(printed: Printed, command: MaterialRemove):
    state = State.collect(printed.path, read_materials=True)

    if command.name not in state.materials:
        material_names = ", ".join(state.materials)
        raise cappa.Exit(f"Material '{command.name}' not found from: {material_names}.")

    state.materials.pop(command.name)

    state.write_materials()
