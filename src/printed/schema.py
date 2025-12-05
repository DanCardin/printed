from __future__ import annotations

import logging
import shutil
from collections.abc import Iterator
from pathlib import Path, PurePath
from typing import BinaryIO, ClassVar, Literal, Self, TypeAlias, assert_never, cast
from urllib.parse import urlparse

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)
from whenever import OffsetDateTime, TimeDelta

from printed.formatting import parse_duration
from printed.path import get_content, write_content

log = logging.getLogger(__name__)

model_config = ConfigDict(arbitrary_types_allowed=True)


class Investment(BaseModel):
    model_config: ClassVar[ConfigDict] = model_config

    description: str
    cost: float


OrderOptions: TypeAlias = Literal["created_at", "count", "name", "saved"]


class PrintStore(BaseModel):
    model_config: ClassVar[ConfigDict] = model_config

    path: Path

    print_paths: dict[str, Path] = Field(default_factory=dict)
    prints: dict[str, Print] = Field(default_factory=dict)
    cached: set[str] = Field(default_factory=set)

    @classmethod
    def collect(cls, path: Path):
        instance = cls(path=path)
        instance.refresh()
        return instance

    def __iter__(self) -> Iterator[Print]:
        for print in self.print_paths:
            yield self[print]

    def __contains__(self, name: str) -> bool:
        return name in self.print_paths

    def __getitem__(self, name: str) -> Print:
        if name in self.cached:
            return self.prints[name]

        print = Print.collect(self.path, name)
        self.cached.add(name)
        self.prints[name] = print
        return print

    def invalidate(self):
        self.cached = set()

    def refresh(self):
        self.print_paths = {}
        for child_path in self.path.iterdir():
            if not child_path.is_dir():
                continue

            name = child_path.name
            self.print_paths[name] = child_path

    def add(self, print: Print) -> Print:
        name = print.name
        path = self.path / name
        print.path = path
        self.prints[name] = print
        self.print_paths[name] = path
        self.cached.add(name)
        return print

    def get(self, name: str) -> Print | None:
        if name not in self:
            return None

        return self[name]

    def write(self, name: str):
        self.prints[name].write()


class State(BaseModel):
    model_config: ClassVar[ConfigDict] = model_config

    path: Path

    prints: PrintStore
    investments: list[Investment] = Field(default_factory=list)
    materials: dict[str, Material] = Field(default_factory=dict)

    INVESTMENTS_FILE: ClassVar[PurePath] = PurePath("investments.toml")
    MATERIALS_FILE: ClassVar[PurePath] = PurePath("materials.toml")

    order_options: ClassVar[list[OrderOptions]] = [
        "created_at",
        "count",
        "name",
        "saved",
    ]

    @classmethod
    def investments_path(cls, path: Path):
        return path / cls.INVESTMENTS_FILE

    @classmethod
    def materials_path(cls, path: Path):
        return path / cls.MATERIALS_FILE

    def write_materials(self):
        write_content(self.path, dict[str, Material], self.materials)

    @classmethod
    def collect_all(cls, path: Path):
        return cls.collect(path, read_investments=True, read_materials=True)

    @classmethod
    def collect(
        cls, path: Path, read_investments: bool = False, read_materials: bool = False
    ):
        investments: list[Investment] = []
        if read_investments:
            investments = get_content(
                cls.investments_path(path),
                dict[str, list[Investment]],
                default={"investment": []},
            )["investment"]

        materials = {}
        if read_materials:
            materials = get_content(
                cls.materials_path(path),
                dict[str, Material],
                default=materials,
            )

        return cls(
            path=path,
            investments=investments,
            materials=materials,
            prints=PrintStore.collect(path),
        )

    def get_prints(
        self,
        order: OrderOptions,
        direction: Literal["asc", "desc"],
        filter: Literal["all", "printed", "unprinted"],
    ):
        def by(print: Print):
            match order:
                case "created_at":
                    return print.created_at
                case "count":
                    return print.count
                case "saved":
                    return print.total_saved
                case "name" | _:
                    return print.title
            assert_never(order)

        filtered_result = [
            p
            for p in self.prints
            if (not filter or filter == "all")
            or (filter == "printed" and p.count)
            or (filter == "unprinted" and not p.count)
        ]

        reverse = direction == "desc"
        return sorted(filtered_result, key=by, reverse=reverse)

    def get_materials(
        self,
        order: Literal["name", "unit", "price_per_unit"],
        direction: Literal["asc", "desc"],
    ):
        def by(print: Material):
            match order:
                case "unit":
                    return print.unit
                case "price_per_unit":
                    return print.price_per_unit
                case "name" | _:
                    return print.name

            assert_never(order)

        reverse = direction == "desc"
        return sorted(self.materials.values(), key=by, reverse=reverse)

    @property
    def material_names(self) -> str:
        return ", ".join(self.materials)

    @property
    def total_investment(self):
        return sum(i.cost for i in self.investments)

    @property
    def total_reference_cost(self) -> float:
        return sum(p.reference_cost for p in self.prints)

    @property
    def total_weight(self) -> float:
        return sum(p.weight for p in self.prints)

    @property
    def total_cost(self) -> float:
        return sum(p.cost for p in self.prints)

    @property
    def total_print_time(self) -> TimeDelta:
        return sum((p.duration for p in self.prints), start=TimeDelta())

    @property
    def total_count(self) -> int:
        return sum(p.count for p in self.prints)

    @property
    def total_printed_weight(self) -> float:
        return sum(p.total_printed_weight for p in self.prints)

    @property
    def total_printed_cost(self) -> float:
        return sum(p.total_printed_cost for p in self.prints)

    @property
    def total_saved(self) -> float:
        return sum(p.total_saved for p in self.prints)

    @property
    def grand_total_saved(self) -> float:
        return self.total_saved - self.total_investment


class Print(BaseModel):
    model_config: ClassVar[ConfigDict] = model_config

    name: str
    title: str

    reference_cost: float = 0.0

    duration: TimeDelta = Field(default_factory=TimeDelta)
    created_at: OffsetDateTime = Field(
        default_factory=lambda: OffsetDateTime.now(0, ignore_dst=True)
    )

    source_links: list[Link] = Field(default_factory=list)
    reference_links: list[Link] = Field(default_factory=list)
    materials: list[PrintMaterial] = Field(default_factory=list)
    history: list[PrintHistory] = Field(default_factory=list)

    path: Path = Field(default=Path(), exclude=True)

    SETTINGS_FILE: ClassVar[PurePath] = PurePath("project.toml")

    @field_validator("duration", mode="plain")
    @classmethod
    def validate_duration(cls, data: str | TimeDelta):
        if isinstance(data, TimeDelta):
            return data

        return TimeDelta.parse_common_iso(data)

    @field_serializer("duration")
    @staticmethod
    def serialize_duration(duration: TimeDelta):
        return duration.format_common_iso()

    @field_validator("created_at", mode="plain")
    @classmethod
    def validate_created_at(cls, data: str) -> OffsetDateTime:
        return OffsetDateTime.parse_common_iso(data)

    @field_serializer("created_at")
    @staticmethod
    def serialize_created_at(created_at: TimeDelta):
        return created_at.format_common_iso()

    @classmethod
    def collect(cls, path: Path, name: str):
        print_path = path / name
        settings_path = print_path / cls.SETTINGS_FILE
        result = get_content(settings_path, cls)
        result.path = print_path
        return result

    @property
    def count(self):
        return len(self.history)

    @property
    def weight(self):
        return sum(pm.unit_count for pm in self.materials)

    @property
    def cost(self):
        return sum(pm.unit_count * pm.price_per_unit for pm in self.materials)

    @property
    def total_printed_weight(self):
        return self.weight * self.count

    @property
    def total_printed_cost(self):
        return self.cost * self.count

    @property
    def total_reference_cost(self):
        return self.reference_cost * self.count

    @property
    def total_saved(self):
        return self.total_reference_cost - self.total_printed_cost

    @property
    def files(self):
        return {
            path.name: PrintFile(path=path)
            for path in self.path.iterdir()
            if path.suffix.lower() in {".stl", ".3mf", ".obj"}
        }

    @property
    def filenames(self) -> list[str]:
        return [f.filename for f in self.files.values()]

    def write(self):
        write_content(self.path / self.SETTINGS_FILE, Print, self)

    def delete(self):
        return

    def update(
        self,
        *,
        reference_cost: float,
        duration: str,
        source_links: list[tuple[str, str]],
        reference_links: list[tuple[str, str]],
        materials: dict[str, float],
    ):
        self.reference_cost = reference_cost
        if duration:
            self.duration = parse_duration(duration)
        self.source_links = [Link(url=url, title=title) for url, title in source_links]
        self.reference_links = [
            Link(url=url, title=title) for url, title in reference_links
        ]

        for m in self.materials:
            material_amount = materials.get(m.material)
            if material_amount is not None:
                m.unit_count = material_amount

    def append_history(self):
        self.history.insert(0, PrintHistory())
        self.history.sort(key=lambda h: h.printed_on, reverse=True)

    def delete_history(self, number: int):
        self.history.pop(number - 1)

    def append_source_link(self):
        self.source_links.insert(0, Link())
        self.source_links.sort(key=lambda h: h.title)

    def delete_source_link(self, number: int):
        self.source_links.pop(number - 1)

    def append_reference_link(self):
        self.reference_links.insert(0, Link())
        self.reference_links.sort(key=lambda h: h.title)

    def delete_reference_link(self, number: int):
        self.reference_links.pop(number - 1)

    def append_material(self, material: Material):
        self.materials.append(
            PrintMaterial(
                material=material.name, price_per_unit=material.price_per_unit
            )
        )
        self.materials.sort(key=lambda h: h.unit_count)

    def delete_material(self, material_name: str):
        self.materials = [m for m in self.materials if m.material != material_name]

    def add_file(self, filename: str, file: BinaryIO):
        if filename in self.filenames:
            raise ValueError(f"File with name '{filename}' already exists!")

        with open(self.path / filename, "wb+") as file_object:
            shutil.copyfileobj(file, file_object)


class Link(BaseModel):
    model_config: ClassVar[ConfigDict] = model_config

    url: str = ""
    title: str = ""

    @model_validator(mode="before")
    @classmethod
    def validate_title(cls, data: dict) -> dict:
        if isinstance(data, dict):
            url = data.get("url")
            title = data.get("title")
            if not title and url:
                purl = urlparse(url)
                data["title"] = purl.netloc
        return data


class PrintFile(BaseModel):
    model_config: ClassVar[ConfigDict] = model_config

    path: Path

    @property
    def filename(self) -> str:
        return self.path.name

    def preview(self) -> str:
        import trimesh
        import trimesh.scene.scene
        import trimesh.viewer

        try:
            trimesh.util.attach_to_log()
            scene = cast(trimesh.Scene, trimesh.load(self.path, force="scene"))
            result = trimesh.viewer.scene_to_html(scene)
            # result = result.replace(
            #     "new THREE.DirectionalLight(0xffffff,1.75)",
            #     "new THREE.DirectionalLight(0xffffff,3)",
            # )
        except Exception as e:
            log.info(e, exc_info=True)
            return ""
        else:
            return result


class PrintHistory(BaseModel):
    model_config: ClassVar[ConfigDict] = model_config

    printed_on: OffsetDateTime = Field(
        default_factory=lambda: OffsetDateTime.now(0, ignore_dst=True)
    )

    status: Literal["success", "failed"] = "success"

    @field_validator("printed_on", mode="plain")
    @classmethod
    def validate_created_at(cls, data: str) -> OffsetDateTime:
        return OffsetDateTime.parse_common_iso(data)

    @field_serializer("printed_on")
    @staticmethod
    def serialize_created_at(printed_on: OffsetDateTime) -> str:
        return printed_on.format_common_iso()


class PrintMaterial(BaseModel):
    model_config: ClassVar[ConfigDict] = model_config

    material: str
    price_per_unit: float
    unit_count: float = 0

    @property
    def price(self) -> float:
        return self.unit_count * self.price_per_unit


class Material(BaseModel):
    model_config: ClassVar[ConfigDict] = model_config

    name: str
    unit: str
    price_per_unit: float = 0.0

    @classmethod
    def from_thousand(cls, name: str, unit: str, value: float, price: float) -> Self:
        price_per_unit = price / (value * 1000)
        return cls(name=name, unit=unit, price_per_unit=price_per_unit)
